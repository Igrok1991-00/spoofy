#!/bin/python3
import os
import sys
import struct
import socket
import readline
from tabulate import tabulate
# import json
import re
import importlib.machinery


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Spoofy(object):
    def __init__(self):
        super(Spoofy, self).__init__()
        self.rhosts = list()
        self.script_lib = list()
        for file in os.listdir("./scripts/"):
            if ".py" in file:
                self.script_lib.append(file)
        self.script_run = dict()
        opt = ["set rhost ", "set script ", "add rhost ", "add script ",
               "show info", "show script", "help", "exit", "run"]
        completer = Completer(opt, self.script_lib)
        readline.set_completer(completer.complete)
        readline.set_completer_delims('')
        readline.parse_and_bind("tab: complete")

    def run(self):
        while True:
            try:
                stdin = self.input_wp('> ').lower()
                mode, parameters = self.parseInput(stdin)

                if mode in ["set rhost", "set rhosts"]:
                    self.rhosts = parameters

                elif mode in ["add rhost", "add rhosts"]:
                    self.rhosts.extend(parameters)

                elif mode in ["set script"]:
                    self.script_run = dict()
                    try:
                        for script in parameters:
                            hook = self.script_run[script] = importlib.machinery.SourceFileLoader(parameters[0], "./scripts/" + parameters[0] ).load_module()
                            self.script_run[script] = hook
                    except Exception as e:
                        print(e)

                elif mode in ['h', 'help']:
                    print(bcolors.HEADER + "Commands\n" + bcolors.ENDC +
                                           " \r set rhost <ip>\n \
                                             \r add rhost <ip>\n \
                                             \r run\n \
                                             \r show <info|script>\n \
                                             \r help\n \
                                             \r close")

                elif mode in ["show info"]:
                    print(bcolors.HEADER + "RHOSTS" + bcolors.ENDC)
                    if len(self.rhosts) >= 1:
                        for host in self.rhosts:
                            print(" ", host)
                    else:
                        print(bcolors.FAIL + " None" + bcolors.ENDC)

                elif mode in ["show script", "show scripts"]:
                    print(bcolors.HEADER + "AVAILABLE" + bcolors.ENDC)
                    print(' '.join(self.script_lib))
                    print(bcolors.HEADER + "\nSELECTED" + bcolors.ENDC)
                    if len(self.script_run) < 1:
                        print(bcolors.FAIL + " None" + bcolors.ENDC)
                    else:
                        print(bcolors.OKGREEN + ' '.join(self.script_run) + bcolors.ENDC)

                elif mode in ["run"]:
                    rows, columns = os.popen('stty size', 'r').read().split()
                    for module in self.script_run:
                        print(bcolors.HEADER + "{0}".format(module) + bcolors.ENDC)
                        output = self.script_run[module].run(self.rhosts)
                        for key in output:
                            data = output[key]
                            print('\n' + key)
                            print(tabulate(data, headers=self.script_run[module].data_headers))

                elif mode in ["exit", "close"]:
                    sys.exit(0)

                elif len(mode) > 0:
                    print(bcolors.FAIL + "Error" + bcolors.ENDC)

            except KeyboardInterrupt:
                print("\n")
                sys.exit(0)

    def parseInput(self, stdin):
        stdin = stdin.split(' ')
        mode = ' '.join(stdin[:2]).lower()
        if mode in ["set rhost", "add rhost"]:
            ipv4 = list()
            networks = stdin[2:]

            for network in networks:
                is_ipv4 = re.match("((?:(?:\d{1,3}\.){3}\d{1,3}))", network)
                if is_ipv4:
                    try:
                        # Determine if a string is a valid IP address
                        # and if so, append it to rhosts
                        socket.inet_aton(network.split('/')[0])
                        ipv4.append(network)
                    except socket.error:
                        print(bcolors.FAIL + "{0} is not a valid address".format(network) + bcolors.ENDC)
                        pass
                else:
                    ipv4.append(network)

            return(mode, ipv4)
        elif mode in ["set script", "add script"]:
            return mode, stdin[2:]
        else:
            return mode, None

    def input_wp(text, prompt):
        def hook():
            readline.insert_text(text)
            readline.redisplay()
        readline.set_pre_input_hook(hook)
        result = input(prompt)
        readline.set_pre_input_hook()
        return result


class Completer(object):  # Custom completer

    def __init__(self, options, scripts):
        self.options = sorted(options)
        self.scripts = sorted(scripts)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if not text:
                self.matches = self.options[:]
            else:
                self.matches = [s for s in self.options
                                if s and s.startswith(text)]
            if text in ["set script ", "add script "]:
                self.matches += [s for s in self.scripts if s]

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


if __name__ == '__main__':
    Spoofy().run()
