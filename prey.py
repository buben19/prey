#!/usr/bin/env python
from src import config
from src import shedule
from src import generator
from src.nmap import nmap
from src.services import ServiceProvider, registerServices
from src.webcrawler import webcrawler
import twisted.internet.reactor

def getArgs():
    pass

def main():
    config.Config.initialize(getArgs())
    registerServices()

    sheduler = ServiceProvider.getInstance().getService(shedule.Sheduler)
    sheduler.installProcess(
        nmap.RandomNmapSupervisor(
            generator.PublicIPV4AddressGenerator(
                generator.RandomIPV4AddressGenerator())),
        1)

    sheduler.installProcess(
        nmap.QueuedNmapSupervisor(),
        1)

    sheduler.installProcess(
        webcrawler.WebCrawlerSupervisor(),
        1)

    # debug
    #import src.url as url
    #sheduler.getProcess(webcrawler.WebCrawlerSupervisor).get(
    #        url.Url("http://seznam.cz/"))

    sheduler.sheduleNext()
    twisted.internet.reactor.run()

if __name__ == '__main__':
    main()
