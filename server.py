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

    def compose_msg(self, output):
        response = ""
        for line in output:
            response += "{}{}\n".format(line[0], line[1])
        return response
    
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
        lines = [ 
                (   "JOINED_CHATROOM: ",        parsed_data["JOIN_CHATROOM"]     ),
                (   "SERVER_IP: ",              str(ipgetter.myip())             ),
                (   "PORT: ",                   self.server.server_address[1]    ),
                (   "ROOM_REF: ",               23                               ),
                (   "JOIN_ID: ",                123                              )
                ]
        return self.compose_msg(lines)
        

    def leave_chatroom(self, data, dataLines):
        parsed_data = { "JOIN_ID" : None, "CLIENT_NAME" : None, "LEAVE_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        lines = [
                (   "LEFT_CHATROOM: ",          parsed_data["LEAVE_CHATROOM"]   ),
                (   "JOIN_ID: ",                parsed_data["JOIN_ID"]          ),
                (   "CLIENT_NAME: ",            parsed_data["CLIENT_NAME"]      )
                ]
        return self.compose_msg(lines)
    

    def chat (self, data, dataLines):
        parsed_data = { "CHAT" : None, "JOIN_ID" : None, "CLIENT_NAME" : None, "MESSAGE" : None }
        parsed_data = self.parseData(dataLines, parsed_data)
        print (parsed_data["MESSAGE"])
        lines = [
                (   "CHAT: ",                   parsed_data["CHAT"]             ),
                (   "CLIENT_NAME: ",            parsed_data["CLIENT_NAME"]      ),
                (   "MESSAGE: ",                parsed_data["MESSAGE"]          )
                ]
        return self.compose_msg(lines)
    

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
        lines = [
                (   data,                    ""                                 ),
                (   "IP: ",                  str(ipgetter.myip())               ),
                (   "Port: ",                self.server.server_address[1]      ),
                (   "StudentID: ",           12302202                           )
                ]
        # response = data + "IP:[{}]\nPort:[{}]\nStudentID:[{}]\n".format(self.server.server_address[0], self.server.server_address[1], 12302202)
        return self.compose_msg(lines)


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    # pass
    
    # def __init__(self, server_address, request_hanler):

    #     print ("initing")
class charRoom ():
    def initialise(self):
        self.num_rooms = 0
        self.num_clients = 0
        self.room2ref = {}
        self.ref2room = {}
        self.ref2id = {}
        self.id2ref = {}
        self.id2name = {}
        self.name2id = {}
        self.roomLock = threading.Lock()
        self.clientLock = threading.Lock()

    def join_chatroom(self, parsed_data):
        ref = self.getRoom(parsed_data["JOIN_ROOM"])
        cID = self.getClient(parsed_data["CLIENT_NAME"])
        return self.addToRoom(ref, client)
    def add2room(self, ref, cID):
        if cID in self.ref2id[ref] or ref in self.id2ref[cID]:
            return 1
        else:
            self.ref2id[ref].append(cID)
            self.id2ref[cID].append(ref)
            return 0

    def leave_chatroom(self, parsed_data):
        ref = parsed_data["LEAVE_CHATROOM"]
        cID = parsed_data["JOIN_ID"]
        if ref in self.ref2id and cID in self.ref2id[ref]:
            self.ref2id[ref].remove(cID)
        else:
            return 1
        if cId in self.id2ref and ref in self.id2ref[cID]:
            self.id2ref[cID].remove(ref)
        else:
            return 2
        return 0

    def disconnect_from_server(self, parsed_data):
        name = parsed_data["CLIENT_NAME"]
        if name in self.name2id:
            cID = self.name2id[name]
            parsed_data["JOIN_ID"] = cID
            issues = 0 
            if cID in self.id2ref:
                for room in self.id2ref[cID]:
                    parsed_data["LEAVE_CHATROOM"] = room
                    issues += leave_chatroom(parsed_data)
                self.name2id.remove(name)
                self.id2name.remoce(cID)
                if issues == 0:
                    return 0
                else:
                    return 3
            else:
                return 1
        else:
            return 2

    def getRoom(self, room_name):
        if room_name in self.room2ref:
            return self.room2ref[room_name]
        else:
            return self.createRoom(room_name)
    def getClient(self, client_name):
        if client_name in self.name2id:
            return self.name2id[client_name]
        else:
            return self.createClient(client_name)

    def createRoom(self, room_name):
        self.room2ref[room_name] = self.num_rooms
        self.ref2room[self.num_rooms] = room_name
        self.ref2id[self.num_rooms] = []
        self.num_rooms += 1
        return self.num_rooms - 1
    def createClient(self, client_name):
        self.name2id[client_name] = self.num_clients
        self.id2name[self.num_clients] = client_name
        self.id2ref = []
        self.num_clients += 1
        return num_clients - 1

    # def actually_chat(self, parsed_data):
    #     response = ""
    #     response += "CHAT: {}\n".format(parsed_data["CHAT"])
    #     response += "CLIENT_NAME: {}\n".format(parsed_data["CLIENT_NAME"])
    #     response += "MESSAGE: {}".format(parsed_data["MESSAGE"])
    #     return response
    # def actually_leave(self, parsed_data):
    #     response = ""
    #     response += "LEFT_CHATROOM: {}\n".format(parsed_data["LEAVE_CHATROOM"])
    #     response += "JOIN_ID: {}\n".format(231)
    #     response += "CLIENT_NAME: {}".format("Dunno")
    #     return response
    # def actually_join(self, parsed_data):
    #     response = ""
    #     response += "JOINED_CHATROOM: {}\n".format(parsed_data["JOIN_CHATROOM"])
    #     IP = str(ipgetter.myip())
    #     # print (IP)
    #     response += "SERVER_IP: {}\n".format(IP)
    #     response += "PORT: {}\n".format(self.server.server_address[1])
    #     response += "ROOM_REF: {}\n".format(23)
    #     response += "JOIN_ID: {}".format(231)
    #     return response
