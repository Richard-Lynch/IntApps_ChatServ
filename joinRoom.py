#!/usr/local/bin/python3


from client import client
import sys
ip = "localhost"
message = "\
        JOIN_CHATROOM: helloWorld
        CLIENT_IP: 0
        PORT: 0
        CLIENT_NAME: Richie"
if len(sys.argv) > 1:
    print ("Port: ", sys.argv[1])
    port = int(sys.argv[1])
    if len(sys.argv) > 2:
        ip = str(sys.argv[2])
else:
    print ("port number needed")
    exit()

client (ip, port, message)

