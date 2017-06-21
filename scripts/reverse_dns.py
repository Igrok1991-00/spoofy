#!/bin/python3
import socket


def run(rhosts):
    return(reverse_dns(rhosts))


def reverse_dns(rhosts):
    hosts = getHostname(rhosts)
    output = ("\nresolved\n----------\n")
    if len(hosts["known"]) < 1:
        output += "None\n"
    else:
        for host in hosts["known"]:
            output += "{0} : {1}\n".format(host[0].ljust(15, ' '),
                                           host[1])
    output += ("\nunresolved\n----------\n")
    if len(hosts["unknown"]) < 1:
        output += "None\n"
    else:
        for host in hosts["unknown"]:
            output += "{0} : {1}".format(host.ljust(15, ' '),
                                         "Unknown")
    return output


def getHostname(rhosts):
        hostList = {"known": list(), "unknown": list()}
        for addr in rhosts:
            try:
                hostname = socket.gethostbyaddr(addr)
                hostList["known"].append((addr, hostname[0]))
            except Exception as e:
                hostList["unknown"].append(addr)
        return hostList
