#!/usr/local/bin/python3
# async.py

import socket
import threading
from threading import Thread
import socketserver as SocketServer
import ipgetter

# from mainLoop import stopServe



class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        commands = {'KILL_SERVICE' : self.kill_service, 'HELO' : self.helo_info, 'JOIN_CHATROOM:' : self.join_chatroom, 'LEAVE_CHATROOM:' : self.leave_chatroom } 
        data = self.request.recv(1024).decode()
        cur_thread = threading.current_thread()
        print ("data:", data, type(data))
        dataLines = self.parseLines(data)
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

    def parseLines(self, dataString):
        lineList = dataString.splitlines()
        print (lineList)
        return lineList

    def parseCommands(self, firstLine):
        pieces = firstLine.split()
        print ("Pieces:", pieces)
        return pieces
    
    def parseData(self, dataLines, expected):
        for key in expected:
            for line in dataLines:
                if key in line:
                    expected[key] = self.parseCommands(line)[1]
        return expected

    def join_chatroom(self, data, dataLines):
        parsed_data = { "CLIENT_IP" : None, "PORT" : None, "CLIENT_NAME" : None, "JOIN_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        response = ""
        for label in parsed_data:
            response += "{}: {}, ".format(label, parsed_data[label])
        # return response[:-2]
        return self.actually_join(parsed_data)
        
    def actually_join(self, parsed_data):
        response = ""
        response += "JOINED_CHATROOM: {}\n".format(parsed_data["JOIN_CHATROOM"])
        # IP = ipgetter.myip()
        response += "SERVER_IP: {}\n".format(self.server.server_address[0])
        response += "PORT: {}\n".format(self.server.server_address[1])
        response += "ROOM_REF: {}\n".format(23)
        response += "JOIN_ID: {}\n".format(231)
        return response

    def leave_chatroom(self, data, dataLines):
        expected = { "JOIN_ID" : None, "CLIENT_NAME" : None, "LEAVE_CHATROOM" : None } 
        expected = self.parseData(dataLines, expected)
        response = ""
        for label in expected:
            response += "{}: {}, ".format(label, expected[label])
        return response[:-2]

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

