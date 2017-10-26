#!/usr/local/bin/python3
# async.py

import socket
import threading
from threading import Thread
import socketserver as SocketServer

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024).decode()
        cur_thread = threading.current_thread()
        if "KILL_SERVICE\n" == data:
            response = "Server is going down, run it again manually!"
            self.server.shutdown()
        elif "HELO text\n" == data:
            response = data + "IP:[{}]\nPort:[{}]\nStudentID:[{}]\n".format(self.server.server_address[0], self.server.server_address[1], 12302202)
        else:
            response = "{}: {}".format(cur_thread.name, data)
        response = response.encode()
        self.request.sendall(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

