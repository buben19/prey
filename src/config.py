from __future__ import unicode_literals
import error

class Defaults(object):
    """
    defaul configuration values
    """

    PROCESS_PATH = "/usr/bin/nmap"
    PROCESS_ARGS = ("-A",)
    OUTPUT_FILE_DIRECTORY = "/tmp"
    MAX_TASKS = 30                      # maximum of running tasks in paralel

    #DB_MODULE = "pyPgSQL.PgSQL"
    DB_MODULE = "psycopg2"
    DB_HOST = "localhost"
    DB_NAME = "prey_test_db"
    DB_USER = "prey"
    DB_PASS = "heslo"

    NMAP_MAX_TASKS = 3

    WEB_CRAWLER_SCAN_LEVEL = 0

class ConfigType(type):

    __initialized = False

    @classmethod
    def initialize(cls, args):
        cls.__initialized = True

    @classmethod
    def __getConfig(cls):
        """
        get some configuration information
        """
        if not cls.__initialized:
            raise error.ConfigError, "configuration isn't initialized"

    @classmethod
    def __getProperty(cls, name):
        if hasattr(cls, "_" + cls.__name__ + "__" + name):
            cls.__getConfig()
            return getattr(cls, "_" + cls.__name__ + "__" + name)()
        else:
            raise AttributeError, "%s isn't config property" % (name,)

    def __getattr__(cls, name):
        return cls.__getProperty(name)

    @classmethod
    def __processPath(cls):
        return Defaults.PROCESS_PATH

    @classmethod
    def __processArgs(cls):
        """
        get generic process args
        """
        return Defaults.PROCESS_ARGS

    @classmethod
    def __outputFileDirectory(cls):
        return Defaults.OUTPUT_FILE_DIRECTORY

    @classmethod
    def __numMaxTasks(cls):
        return Defaults.MAX_TASKS

    @classmethod
    def __dbModule(cls):
        return Defaults.DB_MODULE

    @classmethod
    def __dbHost(cls):
        return Defaults.DB_HOST

    @classmethod
    def __dbName(cls):
        return Defaults.DB_NAME

    @classmethod
    def __dbUser(cls):
        return Defaults.DB_USER

    @classmethod
    def __dbPassword(cls):
        return Defaults.DB_PASS

    @classmethod
    def __nmapMaxTasks(cls):
        return Defaults.NMAP_MAX_TASKS

    @classmethod
    def __webCrawlerScanLevel(cls):
        return Defaults.WEB_CRAWLER_SCAN_LEVEL

class Config(object):
    __metaclass__ = ConfigType
