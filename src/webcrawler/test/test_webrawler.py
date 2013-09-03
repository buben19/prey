import twisted.trial.unittest
import src.webcrawler.webcrawler as webcrawler
import src.services as services
import src.url as url
import src.config as config
import src.error as error


class TestWebCrawlerSupervisor(twisted.trial.unittest.TestCase):

    supervisor = None

    def setUp(self):
        config.Config.initialize(None)
        self.supervisor = WebCrawlerSupervisorTestClass()
        self.supervisor.initializeRunningTasksCount()
        

    def tearDown(self):
        self.supervisor = None
        
        import twisted.internet.reactor
        for i in twisted.internet.reactor.getDelayedCalls():
            i.cancel()


    def test_consumer(self):
        u = url.WebUrl('http://twistedmatrix.com/')
        self.assertEquals(self.supervisor.getWaitingTaskCount(), 0)
        services.getUrlDistributor().distribute(u)
        self.assertEquals(self.supervisor.getWaitingTaskCount(), 1)

    def test_my(self):
        self.supervisor._WebCrawlerSupervisor__urls.append(
            url.WebUrl('https://play.google.com/?hl=cs&tab=w8'), 0)
        return self.supervisor.runTask()
        
    def test_my2(self):
        u = url.WebUrl('http://189.192.161.104a/')
        services.getUrlDistributor().distribute(u)
        return self.supervisor.runTask()
        
    def test_my3(self):
        u = url.WebUrl('http://202.8.8.128/')
        services.getUrlDistributor().distribute(u)
        return self.supervisor.runTask()
    
    def test_my4(self):
        u = url.WebUrl('http://108.177.156.123/')
        services.getUrlDistributor().distribute(u)
        return self.supervisor.runTask()

class TestWebVrawlerQueue(twisted.trial.unittest.TestCase):

    queue = None
    
    def setUp(self):
        self.queue = webcrawler.WebCrawlerQueue()
    
    def tearDown(self):
        self.queue = None
    
    def test_contains(self):
        urlStr = "http://www.google.com"
        self.queue.append(url.WebUrl(urlStr), 0)
        self.assertTrue(url.WebUrl(urlStr) in self.queue)

class WebCrawlerSupervisorTestClass(webcrawler.WebCrawlerSupervisor):
    def runTask(self):
        d = twisted.internet.defer.Deferred()
        try:
            u = self._WebCrawlerSupervisor__urls.popleft()

            self.newTask(
                WebCrawlerTaskTestClass(u[0], u[1]), d)
        except IndexError:
            d.errback(error.TaskError())
        return d

    def taskFinished(self, task, result):
        """
        """
        self.runningTasks -= 1
        task.taskDeferred.callback(result)

class WebCrawlerTaskTestClass(webcrawler.WebCrawlerTask):
    def callbackEnded(self, result):
        """
        called after any deferred callback finished
        """
        self.callbackCount -= 1
        if self.callbackCount < 0:
            raise ValueError, "callbackCount should't reach negative value"
        elif self.callbackCount == 0:
            self.supervisor.taskFinished(self, result)
