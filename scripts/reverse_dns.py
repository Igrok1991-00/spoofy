#!/bin/python3
import socket
import struct
import asyncio

data_headers = ['IP', 'HOST']

def run(rhosts):
    # Eloop = asyncio.get_event_loop()
    # loop.call_soon(getHostname, loop)
    # loop.run_forever()
    # loop.close()
    hosts = getHostname(rhosts)
    return hosts


def getHostname(rhosts):
    hostList = {"resolved": list(), "unresolved": list()}
    unres_limit = False
    unres_count = 0
    for addr in rhosts:
        for ip in getIpRange(addr):
            try:
                hostname = socket.gethostbyaddr(ip)
                hostList["resolved"].append([ip, hostname[0]])
            except Exception as e:
                unres_count += 1
                # unres_count = len(hostList["unresolved"])
                if unres_count < 5 and not unres_limit:
                    hostList["unresolved"].append([ip])
                else:
                    unres_limit = True

    hostList["unresolved"].append(['...and {0} more...'.format(unres_count)])
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
