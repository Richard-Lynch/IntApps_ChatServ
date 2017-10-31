#!/usr/local/bin/python3
# async.py

import socket
import threading
from threading import Thread
import socketserver as SocketServer
# from mainLoop import stopServe


def parseLines(dataString):
    lineList = dataString.splitlines()
    print (lineList)
    return lineList

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        commands = {'KILL_SERVICE' : self.kill_service, 'HELO' : self.helo_info, 'JOIN_CHATROOM:' : self.join_chatroom } 
        data = self.request.recv(1024).decode()
        cur_thread = threading.current_thread()
        print ("data:", data, type(data))
        dataLines = parseLines(data)
        firstLine = self.parseCommands(dataLines[0])
        commandMatched = False
        for command in commands:
            if firstLine[0].startswith(str(command)):
                print ("command matched:", commands[command])
                response = commands[command](data, dataLines)
                commandMatched = True
                break
        if commandMatched == False:
            response = "{}: {}".format(cur_thread.name, data) # echo 
        response = response.encode()
        self.request.sendall(response)

    def parseCommands(self, firstLine):
        pieces = firstLine.split()
        print ("Pieces:", pieces)
        return pieces

    def join_chatroom(self, data, dataLines):
        chatroom = self.parseCommands(dataLines[0])[1]
        if "CLIENT_IP" in dataLines[1]:
            client_ip = self.parseCommands(dataLines[1])[1]
        if "PORT" in dataLines[2]:
            client_port = self.parseCommands(dataLines[2])[1]
        if "CLIENT_NAME" in dataLines[3]:
            client_name = self.parseCommands(dataLines[3])[1]
        response = "ROOM: {}, IP: {}, PORT: {}, NAME: {}".format(chatroom, client_ip, client_port, client_name)
        return response


    def kill_service(self, data, dataLines):
        response = "Server is going down, run it again manually!"
        global stopServer
        stopServer = True
        self.server.shutdown()
        return response

    def helo_info(self, data, dataList):
        response = data + "IP:[{}]\nPort:[{}]\nStudentID:[{}]\n".format(self.server.server_address[0], self.server.server_address[1], 12302202)
        return response


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

