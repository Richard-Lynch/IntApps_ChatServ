#!/usr/local/bin/python3


from client import client
import sys
ip = "localhost"
if len(sys.argv) > 1:
    print ("Port: ", sys.argv[1])
    port = int(sys.argv[1])
    if len(sys.argv) > 2:
        ip = str(sys.argv[2])
else:
    print ("port number needed")
    exit()

message = "\
CHAT: 0\n\
JOIN_ID: {}\n\
CLIENT_NAME: Richie\n\
MESSAGE: testing\n".format(port)
client (ip, port, message)

