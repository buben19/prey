from .. import process
from ..services import ServiceProvider
from ..config import Config
from .. import generator
from .. import address
from .. import url
from .. import repository
from .. import data
import os.path
import twisted.internet.protocol
import xml.etree.ElementTree
import collections
import twisted.internet.defer



class NmapSupervisor(process.BaseProcess):

    # track addresses, which are in progress
    # this object have to be sahred between all NmapSupervisor instances
    addressesInProgress = None

    # object for register address sequences
    # addresses int this object will be used in future
    addressRegistration = None

    # repositories
    hostRepository      = None
    portRepository      = None
    hostnameRepository  = None
    serviceRepository   = None
    cpeRepository       = None
    osRepository        = None
    useableRepository   = None

    def __init__(self):
        """
        addressGenerator - IAddressGenerator provider
        """
        self.addressesInProgress = AddressesInProgress.getInstance()
        self.addressRegistration = AddressRegistration.getInstance()

        sp = ServiceProvider.getInstance()
        self.hostRepository = sp.getService(repository.HostRepository)
        self.portRepository = sp.getService(repository.PortRepository)
        self.hostnameRepository = sp.getService(repository.HostnameRepository)
        self.serviceRepository = sp.getService(repository.ServiceRepository)
        self.cpeRepository = sp.getService(repository.CpeRepository)
        self.osRepository = sp.getService(repository.OsRepository)
        self.useableRepository = sp.getService(repository.NmapUseableAddressRepository)

    def addressInProgress(self, address):
        self.addressesInProgress.add(address)

    def addressFinished(self, address):
        self.addressesInProgress.remove(address)

    def taskFinished(self, task):
        """
        hook for removing address from AddressesInProgress
        """
        self.addressesInProgress.remove(task.address)
        process.BaseProcess.taskFinished(self, task)

class RandomNmapSupervisor(NmapSupervisor):
    """
    nmap scanning random addresses
    """

    # object producing addresses
    __addressProducer = None

    # track, how many addresses are currently generating
    # (their tasks aren't started yet but will be very soon)
    __generatingAddressCount = None

    # IAddressGenerator provider
    # object for generating addresses
    __addressGenerator = None

    def __init__(self, addressGenerator):
        NmapSupervisor.__init__(self)
        self.__generatingAddressCount = 0
        self.__addressGenerator = addressGenerator

    def runTask(self):
        d = twisted.internet.defer.Deferred()
        self.__generatingAddressCount += 1
        self.__generateAddress(d)
        return d

    def __generateAddress(self, taskDeferred):
        while True:
            address = self.__addressGenerator.generate()

            # tesi if address isn't currently scanned and not be scanned
            # by some othre nmap in future
            if not address in self.addressesInProgress and \
                    not address in self.addressRegistration:
                self.useableRepository.isUseable(address).addCallback(
                    self.__isUseableResult,
                    address,
                    taskDeferred)
                break

    def __isUseableResult(self, useable, address, taskDeferred):
        if useable:
            self.__generatingAddressCount -= 1
            self.newTask(
                NmapTask(address),
                taskDeferred)
        else:
            self.__generateAddress(taskDeferred)

    def getWaitingTaskCount(self):
        """
        how many tasks are waiting for sheduling

        infinite tasks can be started
        """
        return float('inf')

    def getRunningTaskCount(self):
        """
        return how much tasks are currently running plus generating addresses
        count
        """
        return NmapSupervisor.getRunningTaskCount(self) + self.__generatingAddressCount

    def getMaxTaskCount(self):
        return 1

class QueuedNmapSupervisor(NmapSupervisor):
    """
    nmap consuming address distributor
    """

    # store addresses which will be scanned
    __addressQueue = None

    # store addresses receive via get method
    __getAddresses = None

    def __init__(self):
        NmapSupervisor.__init__(self)
        self.__addressQueue = collections.deque()
        self.__getAddresses = set()

        # register address sequence
        self.addressRegistration.registerAddressSequence(self.__addressQueue)
        self.addressRegistration.registerAddressSequence(self.__getAddresses)

        # register to distributor
        ServiceProvider.getInstance().getService(data.AddressDistributor).registerConsumer(self)

    def runTask(self):
        d = twisted.internet.defer.Deferred()
        self.newTask(
            NmapTask(self.__addressQueue.popleft()),
            d)
        return d

    def getWaitingTaskCount(self):
        """
        how many tasks are waiting for sheduling
        """
        return len(self.__addressQueue)

    def getMaxTaskCount(self):
        return Config.nmapMaxTasks

    def get(self, address):
        print "queued got address:", address
        def c(isUseable, address):
            self.__getAddresses.remove(address)
            if isUseable:
                self.__addressQueue.append(address)
        if not address in self.addressesInProgress and \
                not address in self.addressRegistration:
            self.__getAddresses.add(address)
            self.useableRepository.isUseable(address).addCallback(c, address)

class AddressesInProgress(set):
    """
    store addresses in progress, singleton class
    """

    __instance = None

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

class AddressRegistration(object):
    """
    register address for future use
    """

    # set of sequences with addresses
    __addressSequences = None

    # instance
    __instance = None

    def __init__(self):
        self.__addressSequences = []

    def registerAddressSequence(self, addressSequence):
        self.__addressSequences.append(addressSequence)

    def unregisterAddressSequence(self, addressSequence):
        self.__addressSequences.remove(addressSequence)

    def __contains__(self, address):
        for sequence in self.__addressSequences:
            if address in sequence:
                return True
        return False

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

class NmapTask(process.BaseTask):
    """
    object representing single nmap task
    """

    hostId          = None
    address         = None

    def __init__(self, address):
        self.address = address

    def start(self):
        self.supervisor.addressInProgress(self.address)

        #self.newCallback(
        #    self.addressDeferred,
        #    DeferredNmap())

        args = []
        args.append('nmap')
        args.extend(Config.processArgs)
        args.append("-oX")
        args.append("-")
        args.append(unicode(self.address))

        # create protocol
        protocol = NmapProtocol(self.address)

        # start process
        import twisted.internet.reactor
        twisted.internet.reactor.spawnProcess(
            protocol,
            Config.processPath,
            args)

        # register callback
        self.newCallback(
            protocol.deferred,
            DeferredNmapOutput())

class NmapProtocol(twisted.internet.protocol.ProcessProtocol):
    """
    protocol for nmap handling

    this is actualy task instance
    """

    deferred            = None
    outputStr           = None
    address             = None

    def __init__(self, address):
        self.address = address
        self.deferred = twisted.internet.defer.Deferred()
        self.outputStr = ""

    def makeConnection(self, process):
        print "starting nmap with address:", str(self.address)

    def processExited(self, reason):
        self.deferred.callback(self.__parseOutput())

    def outReceived(self, data):
        self.outputStr += data

    def __parseOutput(self):
        return xml.etree.ElementTree.fromstring(self.outputStr)

#class DeferredNmap(process.DeferredAction):
#
#    def action(self, address):
#        self.task.address = address
#        args = []
#        args.append('nmap')
#        args.extend(Config.processArgs)
#        args.append("-oX")
#        args.append("-")
#        args.append(address)
#
#        # create protocol
#        protocol = NmapProtocol(address)
#
#        # start process
#        import twisted.internet.reactor
#        twisted.internet.reactor.spawnProcess(
#            protocol,
#            Config.processPath,
#            args)
#
#        # register callback
#        self.task.newCallback(
#            protocol.deferred,
#            DeferredNmapOutput())

class DeferredNmapOutput(process.DeferredAction):

    def action(self, rootElement):
        self.task.newCallback(
            self.task.supervisor.hostRepository.generateHostId(),
            DeferredHost(rootElement))

class DeferredHost(process.DeferredAction):

    rootElement         = None

    def __init__(self, rootElement):
        self.rootElement = rootElement

    def __isUp(self):
        """
        determine if scanned host is up
        """
        for runstats in self.rootElement.iter('runstats'):
            return bool(int(runstats.find('hosts').attrib['up']))

    def action(self, hostId):
        self.task.hostId = hostId
        state = self.__isUp()
        d = self.task.supervisor.hostRepository.saveHost(
            hostId,
            self.task.address,
            "up" if state else "down")
        if state:
            self.task.newCallback(
                d,
                DeferredHostUp(
                    self.rootElement))
        else:
            self.task.newCallback(
                d,
                DeferredHostDown())

class DeferredHostUp(process.DeferredAction):
    """
    process live host
    """

    rootElement = None

    def __init__(self, rootElement):
        self.rootElement = rootElement

    def __hostnames(self, host):
        """
        process information about hostnames
        """
        for hostnames in host.iter('hostnames'):
            for hostname in hostnames.iter('hostname'):
                self.task.newCallback(
                    self.task.supervisor.hostnameRepository.saveHostname(
                        self.task.hostId,
                        hostname.attrib['name'],
                        hostname.attrib['type']),
                    DeferredHostname())

    def __ports(self, ports):
        """
        process information about scanned ports
        """
        for port in ports.iter('port'):
            self.__port(port)

    def __port(self, portElement):
        """
        process single port
        """
        state = portElement.find('state')
        d = self.task.supervisor.portRepository.saveScannedPort(
            self.task.hostId,
            portElement.attrib['portid'],
            portElement.attrib['protocol'],
            state.attrib['state'],
            state.attrib['reason'])
        self.task.newCallback(
            d,
            DeferredService(
                portElement.attrib['portid'],
                portElement))
        self.task.newCallback(
            d,
            DeferredScript(
                portElement.attrib['portid'],
                portElement))

    def __os(self, osElement):
        self.task.newCallback(
            self.task.supervisor.osRepository.createOsId(
                self.task.hostId),
            DeferredOs(osElement))

    def action(self, result):
        host = self.rootElement.find('host')
        self.__hostnames(host)
        self.__ports(host.find('ports'))
        self.__os(host.find('os'))

class DeferredOs(process.DeferredAction):

    osElement = None
    osId = None

    def __init__(self, osElement):
        self.osElement = osElement

    def __portused(self, portusedElement):
        self.task.newCallback(
            self.task.supervisor.osRepository.saveUsedPort(
                self.osId,
                portusedElement.attrib['state'],
                portusedElement.attrib['proto'],
                portusedElement.attrib['portid']),
            DeferredOsPortused())

    def __osmatch(self, osmatchElement):
        self.task.newCallback(
            self.task.supervisor.osRepository.generateOsmatchId(),
            DeferredOsOsmatch(
                osmatchElement,
                self.osId))

    def action(self, osId):
        self.osId = osId
        for i in self.osElement.findall('portused'):
            self.__portused(i)
        for i in self.osElement.findall('osmatch'):
            self.__osmatch(i)

class DeferredOsPortused(process.DeferredAction):
    """
    """

class DeferredOsOsmatch(process.DeferredAction):

    osmatchElement = None
    osId = None

    def __init__(self, osmatchElement, osId):
        self.osmatchElement = osmatchElement
        self.osId = osId

    def action(self, osmatchId):
        self.task.newCallback(
            self.task.supervisor.osRepository.saveOsmatch(
                osmatchId,
                self.osId,
                self.osmatchElement.attrib['name'],
                self.osmatchElement.attrib['accuracy'],
                self.osmatchElement.attrib['line']),
           DeferredOsOsclass(
               osmatchId,
               self.osmatchElement))

class DeferredOsOsclass(process.DeferredAction):

    osmatchId = None
    osmatchElement = None

    def __init__(self, osmatchId, osmatchElement):
        self.osmatchId = osmatchId
        self.osmatchElement = osmatchElement

    def __osclass(self, osclassElement):
        self.task.newCallback(
            self.task.supervisor.osRepository.generateOsclassId(),
            DeferredOsOsclassSave(
                self.osmatchId,
                osclassElement))

    def action(self, reason):
        for i in self.osmatchElement.findall('osclass'):
            self.__osclass(i)

class DeferredOsOsclassSave(process.DeferredAction):

    osmatchId = None
    osclassElement = None

    def __init__(self, osmatchId, osclassElement):
        self.osmatchId = osmatchId
        self.osclassElement = osclassElement

    def action(self, osclassId):
        self.task.newCallback(
            self.task.supervisor.osRepository.saveOsclass(
                osclassId,
                self.osmatchId,
                self.osclassElement.attrib['vendor'],
                self.osclassElement.attrib['accuracy'],
                self.osclassElement.attrib['osfamily'],
                self.osclassElement.attrib['osgen'] if 'osgen' in self.osclassElement.attrib else None,
                self.osclassElement.attrib['type'] if 'type' in self.osclassElement.attrib else None),
            DeferredOsCpe(
                osclassId,
                self.osclassElement))

class DeferredOsCpe(process.DeferredAction):

    osclassId = None
    osclassElement = None

    def __init__(self, osclassId, osclassElement):
        self.osclassId = osclassId
        self.osclassElement = osclassElement

    def __cpe(self, cpeElement):
        self.task.newCallback(
            self.task.supervisor.osRepository.saveCpe(
                self.osclassId,
                cpeElement.tag),
            DeferredOsCpeSave())

    def action(self, reason):
        for i in self.osclassElement.findall('cpe'):
            self.__cpe(i)

class DeferredOsCpeSave(process.DeferredAction):
    """
    """

class DeferredHostDown(process.DeferredAction):
    """
    process down host
    """

class DeferredHostname(process.DeferredAction):
    """
    """

class DeferredService(process.DeferredAction):
    """
    save service informatin in deferred
    """

    port            = None
    portElement     = None
    serviceElement  = None

    def __init__(self, port, portElement):
        self.port = port
        self.portElement = portElement
        self.serviceElement = self.portElement.find('service')

    def action(self, result):
        print self.serviceElement.attrib
        self.__processService()
        self.task.newCallback(
            self.task.supervisor.serviceRepository.saveService(
                self.task.hostId,
                self.port,
                self.serviceElement.attrib['name'],
                self.serviceElement.attrib['method'],
                self.serviceElement.attrib['conf'],
                self.serviceElement.attrib['product'] if 'product' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['version'] if 'version' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['hostname'] if 'hostname' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['ostype'] if 'ostype' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['extrainfo'] if 'extrainfo' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['tunnel'] if 'tunnel' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['proto'] if 'proto' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['rpcnum'] if 'rpcnum' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['lowver'] if 'lowver' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['highver'] if 'highver' in self.serviceElement.attrib else None,
                self.serviceElement.attrib['devicetype'] if 'devicetype' in self.serviceElement else None,
                self.serviceElement.attrib['servicefp'] if 'servicefp' in self.serviceElement.attrib else None),
            DeferredCpe(
                self.port,
                self.serviceElement))

    def __processService(self):
        serviceName = self.serviceElement.attrib['name'].lower()
        if serviceName == 'http':
            self.__http()
        elif serviceName == 'https':
            self.__https()

    def __getPort(self):
        return str(self.portElement.attrib['portid'])

    def __http(self):
        p = self.__getPort()
        if p == '80':
            p = ''
        else:
            p = ':' + p
        self.__url(url.Url('http://' + str(self.task.address) + p + '/'))

    def __https(self):
        p = self.__getPort()
        if p == '443':
            p = ''
        else:
            p = ':' + p
        self.__url(url.Url('https://' + str(self.task.address) + p + '/'))

    def __url(self, u):
        ServiceProvider.getInstance().getService(data.UrlDistributor).distribute(u)

class DeferredCpe(process.DeferredAction):

    port            = None
    serviceElement  = None

    def __init__(self, port, serviceElement):
        self.port = port
        self.serviceElement = serviceElement

    def action(self, reason):
        for cpeElement in self.serviceElement.iter('cpe'):
            self.task.newCallback(
                self.task.supervisor.serviceRepository.saveCpe(
                    self.task.hostId,
                    self.port,
                    cpeElement.text),
                DeferredCpeSave())

class DeferredCpeSave(process.DeferredAction):
    """
    """

class DeferredScript(process.DeferredAction):

    port            = None
    portElement     = None

    def __init__(self, port, portElement):
        self.port = port
        self.portElement = portElement

    def action(self, reason):
        for script in self.portElement.iter('script'):

            # check if script run succesfully
            if script.attrib['output'] != 'ERROR: Script execution failed (use -d to debug)':
                self.task.newCallback(
                    self.task.supervisor.portRepository.generateScriptResultId(),
                    DeferredScriptSave(
                        self.port,
                        script))

class DeferredScriptSave(process.DeferredAction):

    port = None
    scriptElement = None

    def __init__(self, port, scriptElement):
        self.port = port
        self.scriptElement = scriptElement

    def action(self, scriptResultId):
        self.task.newCallback(
            self.task.supervisor.portRepository.saveScriptResult(
                scriptResultId,
                self.task.hostId,
                self.port,
                self.scriptElement.attrib['id'],
                self.scriptElement.attrib['output']),
            DeferredScriptElement(
                scriptResultId,
                self.scriptElement))

class DeferredScriptElement(process.DeferredAction):

    scriptResultId = None
    scriptElement = None

    def __init__(self, scriptResultId, scriptElement):
        self.scriptResultId = scriptResultId
        self.scriptElement = scriptElement

    def action(self, result):
        for element in self.scriptElement.iter('elem'):
            self.task.newCallback(
                self.task.supervisor.portRepository.saveScriptResultElement(
                    self.scriptResultId,
                    element.attrib['key'],
                    element.text),
                DeferredScriptElementSave())

class DeferredScriptElementSave(process.DeferredAction):
    """
    """
