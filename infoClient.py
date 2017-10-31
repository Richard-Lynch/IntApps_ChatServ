#!/usr/local/bin/python3

from client import client
import sys

message = "HELO text\n"
if len(sys.argv) > 1:
    print ("Port: ", sys.argv[1])
    port = int(sys.argv[1])
else:
    print ("port number needed")
    exit()

client ('localhost', port, message)
