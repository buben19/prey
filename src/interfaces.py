"""
define basic interfaces
"""

import zope.interface



class IAddressGenerator(zope.interface.Interface):

    def generate():
        """
        generate IPv4 address
        """

class IIPv4AddressGenerator(IAddressGenerator):
    """
    interface for generating IPv4 addresses
    only for type checking
    """

class ISheduler(zope.interface.Interface):
    """
    interface for task sheduling
    """

class IProcessManager(zope.interface.Interface):
    """
    managing running processes
    """

class ITask(zope.interface.Interface):
    """
    basic program execution unit
    """

class IProcess(zope.interface.Interface):
    """
    obbect encapsulating group of tasks
    """

    def runTask():
        """
        run next task
        """

    def runTasks(count):
        """
        """

    def getRunningTaskCount():
        """
        get count of currently running tasks
        """

    def getWaitingTaskCount():
        """
        get count of tasks waiting for sheduling
        """

    def getUnblockers():
        """
        return set of classes which have ability to unlock process
        """

    def newTask(task, taskDeferred):
        """
        create new task
        """

    def initializeRunningTasksCount():
        """
        initialize task counter to 0, this method should call a sheduler only
        """

    def getMaxTaskCount():
        """
        get how many tasks can be runned simultaneusly
        return inf if num of tasks id not limited
        """

class IProducer(zope.interface.Interface):
    """
    produce data
    """

    def registerConsumer(consumer):
        """
        register new consumer
        """

    def unregisterConsumer(consumer):
        """
        unregister current consumer
        """

class IConsumer(zope.interface.Interface):

    def get(data):
        """
        called by IProducer when new data is avalible
        """

class IUseableReference(zope.interface.Interface):
    """
    check, wheather some object can be used or not
    """

    def isUseable(obj):
        """
        return True or Deferred with True if object is useable, false otherwise
        """
