import tools
from config import Config
from services import ServiceProvider



class Sheduler(object):
    """
    task sheduler
    """

    processManager = None
    sheduleAlgorithm = None
    runningTasks = None         # when reach 0, program will exit

    def __init__(self):
        self.__class__.instance = self
        self.processManager = ProcessManager()
        self.sheduleAlgorithm = TaskBalancer(self.processManager)
        self.runningTasks = 0

    def sheduleNext(self):
        """
        shedule next task for execution
        """

        # just select process and tell run task to it
        #for processCls in self.sheduleAlgorithm.select():
        i = self.sheduleAlgorithm.select()
        print "sheduling - %d tasks is running, %d tasks will be dispatched" % (self.runningTasks, len(i))
        for processCls in i:
            self.processManager.getProcess(processCls).runTask().addCallback(
                self.taskFinished)
            self.runningTasks += 1

    def installProcess(self, process, weight):
        """
        install new process into process manager

        process: IProcess provider
        weight: integer number indicating process cardinality
            bigger weight means more process tasks will be sheduled
        """
        self.processManager.insertProcess(process, weight)
        process.initializeRunningTasksCount()

    def taskFinished(self, process):
        """
        called when process task has been finished
        """
        self.runningTasks -= 1
        self.sheduleNext()

    def getProcess(self, processCls):
        """
        get instance of installed process idetifiewd by its class
        """
        return self.processManager.getProcess(processCls)

    def getProcessweight(self, processCls):
        """
        get weight of process specified by its class
        """
        return self.processManager.getProcessWeight(processCls)

    def getRunningTasksCount(self):
        return self.runningTasks

class ProcessManager(object):
    """
    data structure for managing installed processes
    """

    processes = None            # dictionary of processes

    def __init__(self):
        self.processes = {}

    def insertProcess(self, process, weight):
        self.processes[process.__class__] = self.__createProcessEntry(process, weight)

    def removeProcess(self, processCls):
        del self.processes[processCls]

    def getProcess(self, processCls):
        return self.processes[processCls]['process']

    def getProcessWeight(self, processCls):
        return self.processes[processCls]['weight']

    def getAllProcesses(self):
        tmp = []
        for i in self.processes:
            tmp.append(self.processes[i]['process'])
        return tuple(tmp)

    def getAllProcessClasses(self):
        tmp = []
        for i in self.processes:
            tmp.append(i)
        return tuple(tmp)

    def __createProcessEntry(self, process, weight):
        return {'process' : process,
                'weight' :  weight}

class TaskBalancer(object):
    """
    basic implementation of sheduling algorithm
    """

    processManager = None

    def __init__(self, processManager):
        self.processManager = processManager

    def select(self):
        """
        select which tasks should be runned

        return iterable of all processes ready for shedule
        single instance in iterable can apear many times
        """
        sheduler = ServiceProvider.getInstance().getService(Sheduler)
        tmp = tools.ObjectMultiplier()
        for process in self.processManager.getAllProcesses():
            if process.getWaitingTaskCount() > 0 and \
                    process.getRunningTaskCount() < process.getMaxTaskCount():
                if (len(tmp) + sheduler.getRunningTasksCount()) < Config.numMaxTasks:
                    maxTasks = Config.numMaxTasks - (len(tmp) + sheduler.getRunningTasksCount())

                    if maxTasks >= process.getWaitingTaskCount():
                        if process.getMaxTaskCount() < process.getWaitingTaskCount():
                            tmp.add(process.__class__, process.getMaxTaskCount())
                        else:
                            tmp.add(process.__class__, process.getWaitingTaskCount())
                    elif maxTasks >= process.getMaxTaskCount():
                        tmp.add(process.__class__, process.getMaxTaskCount() - process.getRunningTaskCount())
                    elif maxTasks < process.getWaitingTaskCount():
                        tmp.add(process.__class__, maxTasks)
                        break
                    else:
                        tmp.add(process.__class__, process.getWaitingTaskCount())
                else:
                    break
        return tmp
