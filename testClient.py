#!/usr/local/bin/python3

from client import client
import sys

message = "hello world"
if len(sys.argv) > 1:
    print ("Port: ", sys.argv[1])
    port = int(sys.argv[1])
    if len(sys.argv) > 2:
        message = str(sys.argv[2]).replace("\\n", "\n")
else:
    print ("port number needed")
    exit()

client ('localhost', port, message)
