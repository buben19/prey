"""
service registration
"""

import inspect
import shedule
import address
import url
from twisted.enterprise.adbapi import ConnectionPool
import config
import repository
import data



class ServiceProvider(object):

    __instance = None
    __services = None

    def __init__(self):
        self.__services = {}

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def registerService(self, serviceCls, *args, **kwargs):
        """
        Register new service into service provider instance. Service is initialized
        by calling its constructor
        """
        if serviceCls in self.__services:
            raise KeyError, "service is already registered"
        self.__services[serviceCls] = _ServiceInstance(), args, kwargs
        return self

    def getService(self, serviceCls):
        try:
            instanceWrapper, args, kwargs = self.__services[serviceCls]
            if instanceWrapper:
                return instanceWrapper.instance
            else:
                instanceWrapper.instance = self.__initService(serviceCls, args, kwargs)
                return instanceWrapper.instance
        except KeyError:
            raise KeyError, "service with this class isn't registered"

    def __initService(self, serviceCls, args, kwargs):
            tmp = []
            for i in args:
                if isinstance(i, _LookupService):
                    tmp.append(self.getService(i.serviceCls))
                else:
                    tmp.append(i)
            args = tuple(tmp)
            tmp = {}
            for key, value in kwargs.items():
                if isinstance(value, _LookupService):
                    tmp[key] = self.getService(value.serviceCls)
                else:
                    tmp[key] = value
            kwargs = tmp
            return serviceCls(*args, **kwargs)

    def __contains__(self, serviceCls):
        return serviceCls in self.__services

class _ServiceInstance(object):
    """
    wrapper for service instance
    """

    __instance = None

    @property
    def instance(self):
        return self.__instance

    @instance.setter
    def instance(self, instance):
        if self.instance is not None:
            raise ValueError, "instance is already initialized"
        self.__instance = instance

    def __nonzero__(self):
        return self.instance is not None

class _LookupService(object):

    __serviceCls = None

    def __init__(self, serviceCls):
        if not inspect.isclass(serviceCls):
            raise TypeError, "class expected, not %s" % type(serviceCls).__name__
        self.__serviceCls = serviceCls

    @property
    def serviceCls(self):
        return self.__serviceCls

def lookupService(serviceCls):
    """
    Return object representing, that serviceCls is service to pick up
    from ServiceProvider.

    example:
        serviceProvider.registerService(SomeServiceCls, lookupService(AnotherServiceCls))
    """
    return _LookupService(serviceCls)

def registerServices():
    """
    register services into service provider
    calling this function is part of initialization phase of application
    """
    sp = ServiceProvider.getInstance()
    sp.registerService(shedule.Sheduler)
    sp.registerService(ConnectionPool,
                        config.Config.dbModule,
                        host        = config.Config.dbHost,
                        database    = config.Config.dbName,
                        user        = config.Config.dbUser,
                        password    = config.Config.dbPassword)

    # register repositories
    sp.registerService(repository.HostRepository, lookupService(ConnectionPool))
    sp.registerService(repository.PortRepository, lookupService(ConnectionPool))
    sp.registerService(repository.HostnameRepository, lookupService(ConnectionPool))
    sp.registerService(repository.ServiceRepository, lookupService(ConnectionPool), lookupService(repository.CpeRepository))
    sp.registerService(repository.OsRepository, lookupService(ConnectionPool), lookupService(repository.CpeRepository))
    sp.registerService(repository.CpeRepository, lookupService(ConnectionPool))
    sp.registerService(repository.NmapUseableAddressRepository, lookupService(ConnectionPool))
    sp.registerService(repository.WebCrawlerUrlUseableRepository, lookupService(ConnectionPool))
    sp.registerService(repository.UrlRepository, lookupService(ConnectionPool))
    sp.registerService(repository.WWWPageRepository, lookupService(ConnectionPool), lookupService(repository.UrlRepository))

    # data distribution
    sp.registerService(data.AddressDistributor)
    sp.registerService(data.UrlDistributor)
