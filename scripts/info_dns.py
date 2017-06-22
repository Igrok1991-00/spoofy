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
    hostList = {"I": list(), "II": list()}
    unres_limit = False
    unres_count = 0
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    none_c = FAIL + "None" + ENDC
    for addr in rhosts:
        for ip in getIpRange(addr):
            if ip != None:
                data = list()
                try:
                    answer = dns.resolver.query(ip, 'TXT')
                    for rdata in answer:
                        for string in rdata.strings:
                            if "spf" in str(string):
                                data.append(string)
                except:
                    pass

                try:
                    answer = dns.resolver.query('_dmarc.' + ip, 'TXT')
                    for rdata in answer:
                        for string in rdata.strings:
                            if "DMARC" in str(string):
                                data.append(string)
                except:
                    pass

                if len(data) > 1:
                    hostList["I"].append([ip, data[0]])
                    for record in data[1:]:
                        hostList["I"].append([' ', record])
                    continue
                elif len(data) == 1:
                    hostList["I"].append([ip, data])
                    continue
                else:
                    hostList["II"].append([ip, none_c])

            else:
                continue

    if len(hostList["I"]) < 1:
        hostList["I"].append([none_c, none_c])
    if len(hostList["II"]) < 1:
        hostList["II"].append([none_c, none_c])    
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
