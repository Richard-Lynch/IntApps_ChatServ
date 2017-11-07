#!/usr/local/bin/python3
# chat_server.py
import sys
import socket
import select
import ipgetter
import _thread
from chatRoom import chatRoom

class chat_server():
    def __init__(self):
        self.server_commands= {
                'KILL_SERVICE' : self.kill_service, 
                'HELO' : self.helo_info, 
                'JOIN_CHATROOM:' : self.join_chatroom,
                'LEAVE_CHATROOM:' : self.leave_chatroom,
                'DISCONNECT:' : self.disconnect_client,
                'CHAT' : self.chat
                } 

        self.client_commands= {
                'KILL_SERVICE' : self.kill_service, 
                'HELO' : self.helo_info, 
                'JOIN_CHATROOM:' : self.join_chatroom
                } 

        self.HOST = '' 
        self.SOCKET_LIST = []
        self.RECV_BUFFER = 4096 
        self.PORT = 9009
        self.IP = str(ipgetter.myip())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(10)
        self.chat_room = chatRoom()
     
        # add server socket object to the list of readable connections
        self.SOCKET_LIST.append(self.server_socket)
        print ("Chat server started on port " + str(self.PORT))

    def remove_sock(self, sock):
        try:
            print ("trying to remove sock from list")
            if sock in self.SOCKET_LIST:
                self.SOCKET_LIST.remove(sock)
                print ("removed from list")
            else:
                print ("sock not in list")
        except:
            print ("couldnt remove socket from SOCKET_LIST")
        # try:
        #     sock.close()
        #     print ("closed sock")
        # except:
        #     print ("couldnt close sock")
    
    def hand_client_message(self, sock):
        # receiving data from the socket.
        try:
            data = sock.recv(self.RECV_BUFFER).decode()
        except:
            self.remove_sock(sock)
            return
        if data:
            print ("Received:\n{}".format( data ))
            response = self.handle(sock, data)
            if response != None:
                self.respond(sock, response)
        else:
            # at this stage, no data means probably the connection has been broken
            # broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 
            print ("Client (%s, %s) is offline(hand_client)\n" % sock.getsockname())
            # remove the socket that's broken    
            self.remove_sock(sock)

        return True

    def respond(self, sock, response):
        try :
            sock.send(response.encode())
        except :
            # broken socket connection
            print ("Client (%s, %s) is offline(respond)\n" % sock.getsockname())
            sock.close()
            self.remove_sock(sock)

    def handle(self, sock, data):
        dataLines = self.parseLines(data)
        firstLine = self.parseCommands(dataLines[0])
        print ("parsed", dataLines)
        commandMatched = False
        for command in self.server_commands:
            if firstLine[0].startswith(str(command)):
                response = self.server_commands[command](sock, data, dataLines)
                commandMatched = True
                break
        if commandMatched == False:
            print ("no command matched")
            # self.broadcast(self.SOCKET_LIST, sock, '[' + str(sock.getpeername()) + '] \n' + data)
            response = None
        return response

    def starts(self):
        self.run = True
        while self.run == True:
            # get the list sockets which are ready to be read through select
            # 4th arg, time_out  = 0 : poll and never block
            ready_to_read,ready_to_write,in_error = select.select(self.SOCKET_LIST,[],[],0)
          
            for sock in ready_to_read:
                # a new connection request recieved
                if sock == self.server_socket: 
                    #TODO
                    sockfd, addr = self.server_socket.accept()
                    self.SOCKET_LIST.append(sockfd)
                    print ("Client [{}, {}] connected".format( addr[0], addr[1] ))
                # a message from a client, not a new connection
                else:
                    _thread.start_new_thread(self.hand_client_message, (sock, ))
        for sock in self.SOCKET_LIST:
            sock.close()
        # self.server_socket.close()
        
# broadcast chat messages to all connected clients
    def broadcast (self, socket_list, sock, message):
        for socket in socket_list:
            # send the message only to peer
            if socket != self.server_socket and socket != sock:
                try :
                    socket.send(message.encode())
                except :
                    # broken socket connection
                    print ("Client (%s, %s) is offline(broadcast)\n" % sock.getsockname())
                    self.remove_sock(sock)
# util functions 
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
        mkey = None
        for i, line in enumerate(dataLines):
            if msg == True:
                expected[mkey] = "{}\n".format(expected[mkey])
                parsedLine = self.parseCommands(line)
                values = " ".join(parsedLine)
                expected[key] += "{}".format(values)
            else:
                for key in expected:
                    if key in line:
                        parsedLine = self.parseCommands(line)
                        if parsedLine[0].startswith("MESSAGE"):
                            msg = True
                            mkey = key
                        expected[key] = " ".join(parsedLine[1:])
        return expected
    # def parseData(self, dataLines, expected):
    #     msg = False
    #     for i, line in enumerate(dataLines):
    #         for key in expected:
    #             if key in line:
    #                 parsedLine = self.parseCommands(line)
    #                 expected[key] = "{}".format(parsedLine[1])
    #     return expected
# server commands
    def join_chatroom(self, sock, data, dataLines):
        parsed_data = { "CLIENT_IP" : None, "PORT" : None, "CLIENT_NAME" : None, "JOIN_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        ref, cID = self.chat_room.join_chatroom(parsed_data, sock)
        lines = [ 
                (   "JOINED_CHATROOM: ",        parsed_data["JOIN_CHATROOM"]    ),
                (   "SERVER_IP: ",              str(ipgetter.myip())            ),
                (   "PORT: ",                   sock.getsockname()[1]           ),
                (   "ROOM_REF: ",               ref                             ),
                (   "JOIN_ID: ",                cID                             )
                ]
        memberIDs, memberSockets = self.chat_room.getMembers(ref)
        if cID in memberIDs:
            msg = "{} has joined {} room\n".format(parsed_data["CLIENT_NAME"], parsed_data["JOIN_CHATROOM"])
            self.broadcast (memberSockets, sock, msg)
        return self.compose_msg(lines)
    def kill_service(self, sock, data, dataLines):
        response = "Server is going down, run it again manually!"
        self.run = False
        # global stopServer
        # stopServer = True
        # self.server.shutdown()
        return response

    def helo_info(self, sock, data, dataList):
        print ("data :({})".format(data))
        print ("data :({})".format(data[:-1]))
        newData = data[:-1]
        print ("new: ({})".format(newData))
        lines = [
                (   data[:-1],               ""                                 ),
                (   "IP: ",                  self.IP                            ),
                (   "Port: ",                self.PORT                          ),
                (   "StudentID: ",           12302202                           )
                ]
        return self.compose_msg(lines)
# client commands
    def chat (self, sock, data, dataLines):
        parsed_data = { "CHAT" : None, "JOIN_ID" : None, "CLIENT_NAME" : None, "MESSAGE" : None }
        parsed_data = self.parseData(dataLines, parsed_data)
        print (parsed_data["MESSAGE"])
        lines = [
                (   "CHAT: ",                   parsed_data["CHAT"]             ),
                (   "CLIENT_NAME: ",            parsed_data["CLIENT_NAME"]      ),
                (   "MESSAGE: ",                parsed_data["MESSAGE"]          )
                ]
        if parsed_data["JOIN_ID"] != None:
            # room = self.chat_room.findRoom(parsed_data["CHAT"])
            memberIDs, memberSockets = self.chat_room.getMembers(int(parsed_data["CHAT"]))
            if int(parsed_data["JOIN_ID"]) in memberIDs:
                msg = self.compose_msg(lines)
                self.broadcast (memberSockets, sock, msg)
        return None
        # return send, self.compose_msg(lines)

    def leave_chatroom(self, sock, data, dataLines):
        parsed_data = { "JOIN_ID" : None, "CLIENT_NAME" : None, "LEAVE_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        lines = [
                (   "LEFT_CHATROOM: ",          parsed_data["LEAVE_CHATROOM"]   ),
                (   "JOIN_ID: ",                parsed_data["JOIN_ID"]          ),
                (   "CLIENT_NAME: ",            parsed_data["CLIENT_NAME"]      )
                ]
        memberIDs, memberSockets = self.chat_room.getMembers(int(parsed_data["LEAVE_CHATROOM"]))
        response = None
        if int(parsed_data["JOIN_ID"]) in memberIDs:
            msg = "{} has left chatroom {}\n".format(\
                    parsed_data["CLIENT_NAME"], \
                    self.chat_room.rooms[int(parsed_data["LEAVE_CHATROOM"])].name)
            self.broadcast(memberSockets, sock, msg)
            self.chat_room.leave_chatroom(parsed_data, sock)
            response = self.compose_msg(lines)
        return response

    # def leave_chatroom(self):
    #     pass
    def disconnect_client(self):
        pass

if __name__ == "__main__":
    server = chat_server()
    server.starts() 
