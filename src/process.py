from zope.interface import implementer
import interfaces
import services
import twisted.python.failure
import sys



@implementer(interfaces.IProcess)
class BaseProcess(object):

    runningTasks = None

    def initializeRunningTasksCount(self):
        if self.runningTasks is None:
            self.runningTasks = 0
        else:
            raise ValueError, "task counter seems to be already initialized"

    def runTask(self):
        """
        run single task
        return Deferred, when task is finished, deferred is called
        with None
        """

    def runTasks(self, count):
        """
        run number of tasks specified by count
        return tuple of deferreds
        """
        tmp = []
        for i in xrange(count):
            tmp.append(self.runTask())
        return tuple(tmp)

    def taskFinished(self, task):
        """
        """
        self.runningTasks -= 1
        task.taskDeferred.callback(self)

    def unhandledError(self, reason):
        print "UNHANDLED ERROR:"
        reason.printTraceback()
        import twisted.internet.reactor
        twisted.internet.reactor.stop()
        exit(1)

    def getRunningTaskCount(self):
        return self.runningTasks

    def getUnblockers(self):
        """
        return set of classes, which have ability to unblock this process
        """

        # base implementation shoud return empty set
        return set()

    def newTask(self, task, taskDeferred):
        self.runningTasks += 1
        task.injectSupervisor(self)
        task.initializeDeferredCallbacks()
        task.injectTaskDeferred(taskDeferred)
        task.start()

    def getMaxTaskCount(self):
        return float('inf')

class BaseTask(object):
    """
    base class for all tasks
    """

    supervisor = None
    deferredCount = None
    callbackCount = None
    taskDeferred = None

    # track all deferreds and their callback calling
    __deferredCallbacks = None

    def injectSupervisor(self, supervisor):
        self.supervisor = supervisor

    def initializeDeferredCallbacks(self):
        self.__deferredCallbacks = {}

    def injectTaskDeferred(self, taskDeferred):
        self.taskDeferred = taskDeferred

    def start(self):
        """
        implemet task logic here
        """

    def callbackEnded(self, deferred, result):
        """
        called after any deferred callback finished
        """
        self.__decrementCallback(deferred)
        if self.__tryRemoveDeferred(deferred) and isinstance(result, twisted.python.failure.Failure):

            # unhandled error
            self.supervisor.unhandledError(result)
        if not len(self.__deferredCallbacks) > 0:
            self.supervisor.taskFinished(self)

    def newCallback(self, deferred, callback, *args, **kwargs):
        self.__incerementCallback(deferred)
        callback.injectTask(self)
        callback.injectDeferred(deferred)
        deferred.addCallback(callback, *args, **kwargs)

    def newCallbacks(self, deferred, callback, errback, callbackArgs=None, callbackKeywords=None, errbackArgs=None, errbackKeywords=None):
        self.__incerementCallback(deferred)
        callback.injectTask(self)
        callback.injectDeferred(deferred)
        errback.injectTask(self)
        errback.injectDeferred(deferred)
        deferred.addCallbacks(
            callback,
            errback,
            callbackArgs,
            callbackKeywords,
            errbackArgs,
            errbackKeywords)

    def newErrback(self, deferred, errback, *args, **kwargs):
        self.__incerementCallback(deferred)
        errback.injectTask(self)
        errback.injectDeferred(deferred)
        deferred.addErrback(errback, *args, **kwargs)

    def __incerementCallback(self, deferred):
        if not deferred in self.__deferredCallbacks:
            self.__deferredCallbacks[deferred] = 0
        self.__deferredCallbacks[deferred] += 1

    def __decrementCallback(self, deferred):
        self.__deferredCallbacks[deferred] -= 1
        if self.__deferredCallbacks[deferred] < 0:
            raise ValueError, "callbackCount should't reach negative value"

    def __tryRemoveDeferred(self, deferred):
        if not self.__deferredCallbacks[deferred] > 0:
            del self.__deferredCallbacks[deferred]
            return True
        return False

class DeferredAction(object):

    task = None
    __deferred = None

    def injectTask(self, task):
        self.task = task

    def injectDeferred(self, deferred):
        self.__deferred = deferred

    def __call__(self, obj, *args, **kwargs):
        try:
            r = self.action(obj, *args, **kwargs)
        except Exception:
            t, v, tb = sys.exc_info()
            r = twisted.python.failure.Failure(v, t, tb)
        self.task.callbackEnded(self.__deferred, r)
        return r

    def action(self, obj):
        """
        implement callback action here
        """
