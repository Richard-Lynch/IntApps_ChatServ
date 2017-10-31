#!/usr/local/bin/python3
# client.py
import socket
import sys
def client(ip, port, message):
    print ("IP:", ip, type(ip))
    print ("Port:", port, type(port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        print ("Sending: {}".format(message))
        sock.sendall(message.encode())
        response = sock.recv(1024).decode()
        print("Received: \n{}".format(response))
    finally:
        sock.close()

