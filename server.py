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
        commands = {
                'KILL_SERVICE' : self.kill_service, 
                'HELO' : self.helo_info, 
                'JOIN_CHATROOM:' : self.join_chatroom, 
                'LEAVE_CHATROOM:' : self.leave_chatroom,
                'DISCONNECT:' : self.disconnect_client,
                'CHAT' : self.chat
                } 
        
        data = self.request.recv(1024).decode()
        cur_thread = threading.current_thread()
        print ("data:", data, type(data))
        dataLines = self.parseLines(data)
        firstLine = self.parseCommands(dataLines[0])
        commandMatched = False
        for command in commands:
            if firstLine[0].startswith(str(command)):
                # print ("command matched:", commands[command])
                response = commands[command](data, dataLines)
                commandMatched = True
                break
        if commandMatched == False:
            response = "{}: {}".format(cur_thread.name, data) # echo 
        response = response.encode()
        self.request.sendall(response)

    def parseLines(self, dataString):
        lineList = dataString.splitlines()
        # print (lineList)
        return lineList

    def parseCommands(self, firstLine):
        pieces = firstLine.split()
        # print ("Pieces:", pieces)
        return pieces
    
    def parseData(self, dataLines, expected):
        msg = False
        for i, line in enumerate(dataLines):
            if msg == True:
                expected[key] = "{}\n".format(expected[key])
                parsedLine = self.parseCommands(line)
                values = ""
                for value in parsedLine:
                    values += "{} ".format(str(value))
                expected[key] += "{}".format(values)
            else:
                for key in expected:
                    if key in line:
                        parsedLine = self.parseCommands(line)
                        if parsedLine[0].startswith("MESSAGE"):
                            msg = True
                        expected[key] = "{}".format(parsedLine[1])
        return expected

    def join_chatroom(self, data, dataLines):
        parsed_data = { "CLIENT_IP" : None, "PORT" : None, "CLIENT_NAME" : None, "JOIN_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        # response = ""
        # for label in parsed_data:
        #     response += "{}: {}, ".format(label, parsed_data[label])
        # return response[:-2]
        return self.actually_join(parsed_data)
        
    def actually_join(self, parsed_data):
        response = ""
        response += "JOINED_CHATROOM: {}\n".format(parsed_data["JOIN_CHATROOM"])
        IP = str(ipgetter.myip())
        # print (IP)
        response += "SERVER_IP: {}\n".format(IP)
        response += "PORT: {}\n".format(self.server.server_address[1])
        response += "ROOM_REF: {}\n".format(23)
        response += "JOIN_ID: {}\n".format(231)
        return response

    def leave_chatroom(self, data, dataLines):
        parsed_data = { "JOIN_ID" : None, "CLIENT_NAME" : None, "LEAVE_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        # response = ""
        # for label in parsed_data:
        #     response += "{}: {}, ".format(label, parsed_data[label])
        # return response[:-2]
        return self.actually_leave(parsed_data)
    
    def actually_leave(self, parsed_data):
        response = ""
        response += "LEFT_CHATROOM: {}\n".format(parsed_data["LEAVE_CHATROOM"])
        response += "JOIN_ID: {}\n".format(231)
        response += "CLIENT_NAME: {}\n".format("Dunno")
        return response

    def chat (self, data, dataLines):
        parsed_data = { "CHAT" : None, "JOIN_ID" : None, "CLIENT_NAME" : None, "MESSAGE" : None }
        parsed_data = self.parseData(dataLines, parsed_data)
        print (parsed_data["MESSAGE"])
        response = "Terminating Connection"
        return response

    def disconnect_client (self, data, dataLines):
        parsed_data = { "DISCONNECT" : None, "PORT" : None, "CLIENT_NAME" : None }
        parsed_data = self.parseData(dataLines, parsed_data)
        response = "Terminating Connection"
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

