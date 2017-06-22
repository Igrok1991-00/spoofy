#!/bin/python3
import socket
import struct
import asyncio
import json


def run(rhosts):
    hosts = getHostname(rhosts)
    '''
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
    '''
    return hosts


def getHostname(rhosts):
    hostList = {"known": list(), "unknown": list()}
    for addr in rhosts:
        for ip in getIpRange(addr):
            try:
                hostname = socket.gethostbyaddr(ip)
                hostList["known"].append((ip, hostname[0]))
            except Exception as e:
                hostList["unknown"].append(ip)
    return hostList


def getIpRange(rhost):
    try:
        (ip, cidr) = rhost.split('/')
        cidr = int(cidr)
        host_bits = 32 - cidr
        i = struct.unpack('>I', socket.inet_aton(ip))[0]
        start = (i >> host_bits) << host_bits
        end = i | ((1 << host_bits) - 1)
        for i in range(start, end):
            x = (socket.inet_ntoa(struct.pack('>I', i)))
            yield x

    except ValueError:
        ip = rhost
        yield(ip)
