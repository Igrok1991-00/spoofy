#!/bin/python3
import socket
import re
import struct
import dns.resolver
import asyncio

data_headers = ["HOST", "DNS TXT"]


def run(rhosts):
    # Eloop = asyncio.get_event_loop()
    # loop.call_soon(getHostname, loop)
    # loop.run_forever()
    # loop.close()
    hosts = getDnsInfo(rhosts)
    return hosts


def getDnsInfo(rhosts):
    hostList = {"1": list(), "2": list()}
    unres_limit = False
    unres_count = 0
    for addr in rhosts:
        for ip in getIpRange(addr):
            if ip != None:
                try:
                    answers = dns.resolver.query(ip, 'TXT')
                    # print(answers)
                    for rdata in answers:
                        for string in rdata.strings:
                            if "spf" in str(string):
                                dns_txt = string
                            else:
                                raise Exception
                           # print(rdata.strings)
                    # dns_info = socket.getaddrinfo(ip, 0, 0, 0, 0)
                    # print(dns_info)
                    hostList["1"].append([ip, dns_txt])
                except Exception as e:
                    unres_count += 1
                    # unres_count = len(hostList["unresolved"])
                    if unres_count < 5 and not unres_limit:
                        hostList["2"].append([ip, 'None'])
                    else:
                        unres_limit = True
            else:
                continue
    if unres_count > 5:
        hostList["2"].append(['...and {0} more...'.format(unres_count)])
    return hostList


def getIpRange(rhost):
    is_ipv4 = re.match("((?:(?:\d{1,3}\.){3}\d{1,3}))", rhost)
    if is_ipv4:
        try:
            (ip, cidr) = rhost.split('/')
            cidr = int(cidr)
            host_bits = 32 - cidr
            i = struct.unpack('>I', socket.inet_aton(ip))[0]
            start = (i >> host_bits) << host_bits
            end = i | ((1 << host_bits) - 1)
            for i in range(start, end):
                x = (socket.inet_ntoa(struct.pack('>I', i)))
                try:
                    hostname = socket.gethostbyaddr(x)
                    yield(hostname[0])

                except socket.herror:
                    yield None

        except ValueError:
            try:
                hostname = socket.gethostbyaddr(rhost)
                yield(hostname[0])
            except socket.herror:
                yield None

    else:
        yield(rhost)
