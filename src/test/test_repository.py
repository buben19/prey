import twisted.trial.unittest
import src.repository as repository
import twisted.enterprise.adbapi
import src.url as url
import src.address as address
from src.config import Config



class BaseTest(twisted.trial.unittest.TestCase):

    repository = None
    connectionPool = None

    # steps for deleting database
    dbDelete = [
        "url_queries",
        "www_page_error_extras",
        "www_page_fetch_info",
        "www_page_additional_info",
        "http_headers",
        "www_page_located_at_urls",
        "www_pages",
        "urls_resolved_to_hosts",
        "urls",
        "script_result_elements",
        "script_results",
        "service_cpe",
        "services",
        "ports",
        "os_osclass_cpe",
        "os_osclass",
        "os_osmatch",
        "os_used_ports",
        "os",
        "cpe",
        "hostnames",
        "hosts"]

    def setUp(self):
        self.connectionPool = self.__createConnectionPool()
        d = twisted.internet.defer.Deferred()
        def c1(result, deferred):
            deferred.callback(None)
        self.__setUptHook().addCallback(c1, d)
        return d

    def tearDown(self):
        d = twisted.internet.defer.Deferred()
        def c3(result, deferred):
            self.connectionPool = None
            self.repository = None
            deferred.callback(result)
        def c2(result, deferred):
            self.__resetSequences().addCallback(c3, deferred)
        def c1(result, deferred):
            self.__emptyDb().addCallback(c2, deferred)
        self.__tearDownHook().addCallback(c1, d)
        return d

    def __setUptHook(self):
        d = twisted.internet.defer.Deferred()
        def c(result, deferred):
            deferred.callback(result)
        r = self.setUpHook()
        if isinstance(r, twisted.internet.defer.Deferred):
            r.addCallback(c, d)
        else:
            d.callback(None)
        return d

    def __tearDownHook(self):
        d = twisted.internet.defer.Deferred()
        def c(result, deferred):
            deferred.callback(result)
        r = self.tearDownHook()
        if isinstance(r, twisted.internet.defer.Deferred):
            r.addCallback(c, d)
        else:
            d.callback(None)
        return d

    def setUpHook(self):
        pass

    def tearDownHook(self):
        pass

    def __createConnectionPool(self):
        Config.initialize(None)
        return twisted.enterprise.adbapi.ConnectionPool(
            Config.dbModule,
            host = Config.dbHost,
            database = Config.dbName,
            user = Config.dbUser,
            password = Config.dbPassword)

    def __emptyDb(self):
        d = twisted.internet.defer.Deferred()
        def delete(result, iterator, deferred):
            try:
                table = iterator.next()
                self.connectionPool.runOperation("delete from %s" % (table,)).addCallback(
                    delete,
                    iterator,
                    deferred)
            except StopIteration:
                deferred.callback(None)
        twisted.internet.defer.succeed(None).addCallback(delete, self.dbDelete.__iter__(), d)
        return d

    def __resetSequences(self):
        d = twisted.internet.defer.Deferred()
        def c(result, deferred):
            def reset(result, iterator, deferred):
                try:
                    sequence = iterator.next()[0]
                    self.connectionPool.runOperation(
                        "alter sequence %s restart with 1" % (sequence,)).addCallback(reset, iterator, deferred)
                except StopIteration:
                    deferred.callback(None)
            reset(None, result.__iter__(), deferred)
        self.connectionPool.runQuery("select * from pg_class where relkind='S'").addCallback(c, d)
        return d

    def test_my(self):
        d = twisted.internet.defer.Deferred()
        iterator = iter(range(10))
        def c(result, iterator, deferred):
            if result is not None:
                print result[0][0]
            try:
                iterator.next()
                self.connectionPool.runQuery("select nextval('test_seq')").addCallback(c, iterator, deferred)
            except StopIteration:
                deferred.callback(None)
        twisted.internet.defer.succeed(None).addCallback(c, iterator, d)
        return d

    def test_my2(self):
        pass

    def deferred(self):
        return twisted.internet.defer.Deferred()

    def succeed(self, result):
        return twisted.internet.defer.succeed(result)


class TestHostRepository(BaseTest):

    def setUpHook(self):
        self.repository = repository.HostRepository(self.connectionPool)

    def getResults(self):
        return self.connectionPool.runQuery("select * from hosts")

    def test_generateHostId(self):
        d = self.deferred()
        def c(hostId, deferred):
            self.assertEquals(hostId, 1)
            deferred.callback(None)
        self.repository.generateHostId().addCallback(c, d)
        return d

    def test_saveHost(self):
        d = self.deferred()
        def c3(result, deferred):
            print "here", result
            self.assertEquals(len(result), 1)
            self.assertEquals(result[0]['address'], "127.0.0.1")
            deferred.callback(None)
        def c2(result, deferred):
            self.getResults().addCallback(c3, deferred)
        def c1(hostId, deferred):
            self.repository.saveHost(hostId, address.Address("127.0.0.1"), "up").addCallback(c2, deferred)
        self.repository.generateHostId().addCallback(c1, d)
        return d

    def test_my2(self):
        return self.repository.saveHost(7538, '127.0.0.2', 'D')

class TestWebCrawlerUrlUseableRepository(BaseTest):

    def setUp(self):
        self.repository = repository.WebCrawlerUrlUseableRepository(
            self._createConnectionPool())

    def test_true(self):
        def c(result):
            self.assertTrue(result)
        d = self.repository.isUseable(url.WebUrl("http://www.example.com?one=1"))
        d.addCallback(c)
        return d

    def test_false(self):
        def c(result):
            self.assertTrue(result)
        d = self.repository.isUseable(url.WebUrl("http://www.example.com?one=1&two=2"))
        d.addCallback(c)
        return d

class TestUrlRepository(BaseTest):

    def setUp(self):
        self.repository = repository.UrlRepository(
            self._createConnectionPool())

    def test_my(self):
        def c(result):
            print result
        d = self.repository.getUrlsIdSet([
            url.WebUrl("http://google.com"),
            url.WebUrl("http://googlasfeafe.com"),
            url.WebUrl("https://seznma.cz/index.html"),
            url.WebUrl("http://google.com/")])
        d.addCallback(c)
        return d

class TestWWWPageRepository(BaseTest):

    def setUp(self):
        dbpool = self._createConnectionPool()
        self.repository = repository.WWWPageRepository(
            dbpool,
            repository.UrlRepository(dbpool))

    def test_my(self):
        return self.repository.savePage(
            1,
            url.WebUrl("http://www.example.com?one=1&two=2"),
            200,
            "test title")

    def test_isPageFetchedTrue(self):
        def c(result):
            self.assertTrue(result)
        d = self.repository.isPageFetched(url.WebUrl("http://google.com/"))
        d.addCallback(c)
        return d

    def test_isPageFetchedFalse(self):
        def c(result):
            self.assertFalse(result)
        d = self.repository.isPageFetched(url.WebUrl("http://google.com/index.htm"))
        d.addCallback(c)
        return d
