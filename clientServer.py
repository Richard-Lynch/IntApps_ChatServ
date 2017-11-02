#!/usr/local/bin/python3
# async.py

import socket
import threading
from threading import Thread
import socketserver as SocketServer
import socket as sock
import ipgetter
import select
# from chatRoom import chatRoom
# from mainLoop import stopServe

class clientServer():
    def __init__(self, address, chat_room):
        self.chat_room = chat_room
        self.client_socket = sock.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket.bind(address)
        self.client_socket.listen(10)
        self.serve = True
    def kill_server(self):
        self.server = False

    def loop(self):
        while self.serve:
    # ready_to_read,ready_to_write,in_error = select.select([self.client_socket],[],[],0)
    # for sock in ready_to_read:
    #     # process data recieved from client, 
    #     try:
            # receiving data from the socket.
            sock = self.client_socket
            print ("at accept")
            (conn, (ip,port)) = sock.accept()
            print ("at recv")
            RECV_BUFFER = 4096 
            data = conn.recv(RECV_BUFFER)
            print ("after recv")
            if data:
                print ("at handle")
                # there is something in the socket
                self.handle(data)
            else:
                print ("at else")
            conn.close()
                # remove the socket that's broken    
        # exception 
        # except:
        #     print ("loop issue")
        #     self.serve = False
        #     continue
    # self.client_socket.close()
    
    def broadcast (self, message, room):
        for socket in room:
            # send the message only to peer
            if socket != self.client_socket and socket != None:
                try :
                    socket.send(message)
                except :
                    print ("Issue")
                    # broken socket connection
                    socket.close()
    
    def respond (self, message):
        try :
            self.client_socket.send(message)
        except :
            print ("client_socket broken")
            socket.close()

    def handle(self, data):
        commands = {
                'KILL_SERVICE' : self.kill_service, 
                'HELO' : self.helo_info, 
                'JOIN_CHATROOM:' : self.join_chatroom, 
                'LEAVE_CHATROOM:' : self.leave_chatroom,
                'DISCONNECT:' : self.disconnect_client,
                'CHAT' : self.chat
                } 
        
        data = data.decode()
        print ("data:", data, type(data))
        dataLines = self.parseLines(data)
        firstLine = self.parseCommands(dataLines[0])
        commandMatched = False
        response = None
        send = False
        for command in commands:
            if firstLine[0].startswith(str(command)):
                print ("command matched:", commands[command])
                send, response = commands[command](data, dataLines)
                commandMatched = True
                break

        if send == True and response:
            response = response.encode()
            self.respond(response)

    def compose_msg(self, output):
        response = ""
        for line in output:
            response += "{}{}\n".format(line[0], line[1])
        return response
    
    def parseLines(self, dataString):
        lineList = dataString.splitlines()
        return lineList

    def parseCommands(self, firstLine):
        pieces = firstLine.split()
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
        print ("in join_chatroom, cs")
        parsed_data = { "CLIENT_IP" : None, "PORT" : None, "CLIENT_NAME" : None, "JOIN_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        print ("data parsed:", parsed_data)
        # print (type(self.server.chat_room))
        ref, port = self.server.chat_room.join_chatroom(parsed_data)
        print ("ref:", ref)
        print ("port:", port)
        lines = [ 
                (   "JOINED_CHATROOM: ",        parsed_data["JOIN_CHATROOM"]    ),
                (   "SERVER_IP: ",              str(ipgetter.myip())            ),
                (   "PORT: ",                   port                            ),
                (   "ROOM_REF: ",               ref                             ),
                (   "JOIN_ID: ",                port                            )
                ]
        send = True
        room = self.chat_room.findRoom(ref)

        msg = self.compose_msg(lines)
        self.broadcast(msg, room) 
        return send, self.compose_msg(lines)

    def leave_chatroom(self, data, dataLines):
        parsed_data = { "JOIN_ID" : None, "CLIENT_NAME" : None, "LEAVE_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        lines = [
                (   "LEFT_CHATROOM: ",          parsed_data["LEAVE_CHATROOM"]   ),
                (   "JOIN_ID: ",                parsed_data["JOIN_ID"]          ),
                (   "CLIENT_NAME: ",            parsed_data["CLIENT_NAME"]      )
                ]
        self.server.chat_room.leave_chatroom(parsed_data)
        send = False
        room = self.chat_room.findRoom(ref)
        msg = self.compose_msg(lines)
        self.broadcast(msg, room) 
        return send, self.compose_msg(lines)
    

    def chat (self, data, dataLines):
        parsed_data = { "CHAT" : None, "JOIN_ID" : None, "CLIENT_NAME" : None, "MESSAGE" : None }
        parsed_data = self.parseData(dataLines, parsed_data)
        print (parsed_data["MESSAGE"])
        lines = [
                (   "CHAT: ",                   parsed_data["CHAT"]             ),
                # (   "JOIN_ID: ",                parsed_data["JOIN_ID"]          ),
                (   "CLIENT_NAME: ",            parsed_data["CLIENT_NAME"]      ),
                (   "MESSAGE: ",                parsed_data["MESSAGE"]          )
                ]
        send = True
        if parsed_data["JOIN_ID"] != None:
            room = self.chat_room.findRoom(parsed_data["CHAT"])
            msg = self.compose_msg(lines)
            self.broadcast(msg, room) 
        return send, self.compose_msg(lines)

    def disconnect_client (self, data, dataLines):
        parsed_data = { "DISCONNECT" : None, "PORT" : None, "CLIENT_NAME" : None }
        parsed_data = self.parseData(dataLines, parsed_data)
        response = "Terminating Connection"
        return True, response

    def kill_service(self, data, dataLines):
        response = "Server is going down, run it again manually!"
        global stopServer
        stopServer = True
        self.server.shutdown()
        return True, response

    def helo_info(self, data, dataList):
        lines = [
                (   data,                    ""                                 ),
                (   "IP: ",                  str(ipgetter.myip())               ),
                (   "Port: ",                self.server.server_address[1]      ),
                (   "StudentID: ",           12302202                           )
                ]
        # response = data + "IP:[{}]\nPort:[{}]\nStudentID:[{}]\n".format(self.server.server_address[0], self.server.server_address[1], 12302202)
        return True, self.compose_msg(lines)
