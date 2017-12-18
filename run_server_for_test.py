#!/usr/bin/python3
# chat_server.py
import sys
import socket
import select
import ipgetter
import _thread
from chatRoom import chatRoom
import threading
import time 

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
        self.PORT = 9010
        self.IP = str(ipgetter.myip())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.server_socket.settimeout(None)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(50)
        self.chat_room = chatRoom()
        self.threadLock = threading.Lock()
     
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
    
    def hand_client_message(self, sock, num):

        return True

    def respond(self, sock, response):
        print ("Responding with:\n{}".format(response))
        try :
            sock.send(response.encode())
            print ("sent")
        except :
            # broken socket connection
            print ("Client (%s, %s) is offline(respond)\n" % sock.getpeername())
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
                print ("res is:", response)
                commandMatched = True
                break
        if commandMatched == False:
            print ("no command matched")
            # self.broadcast(self.SOCKET_LIST, sock, '[' + str(sock.getpeername()) + '] \n' + data)
            response = None
        if response != None:
            self.respond(sock, response)

    def starts(self):
        self.run = True
        while self.run == True:
            # get the list sockets which are ready to be read through select
            # 4th arg, time_out  = 0 : poll and never block
            self.threadLock.acquire()
            ready_to_read,ready_to_write,in_error = select.select(self.SOCKET_LIST,[],[],0)
            self.threadLock.release()
            i = 0  
            for sock in ready_to_read:
                print ("i:", i)
                i += 1
                # a new connection request recieved
                if sock == self.server_socket: 
                    #TODO
                    sockfd, addr = self.server_socket.accept()
                    # if sockfd not in self.SOCKET_LIST:
                    self.SOCKET_LIST.append(sockfd)
                    print ("Client [{}, {}] connected".format( addr[0], addr[1] ))
                # a message from a client, not a new connection
                else:
                    # receiving data from the socket.
                    try:
                        print ("waiting to recv")
                        data = sock.recv(self.RECV_BUFFER)
                        print ("data:", data)
                        data = data.decode()
                        print ("received on")
                    except Exception as e :
                        print ("ecept in recv", e)
                        self.remove_sock(sock)
                        continue
                    if data:
                        print ("Received:\n\'{}\'".format( data ))
                        # response = self.handle(sock, data)
                        _thread.start_new_thread(self.handle, (sock, data))
                    else:
                        print ("Blank message received on thisnum")
                        # at this stage, no data means probably the connection has been broken
                        # remove the socket that's broken    
                        self.remove_sock(sock)
        print ("killing")
        for sock in self.SOCKET_LIST:
            sock.close()
        # self.server_socket.close()
        
# broadcast chat messages to all connected clients
    def broadcast (self, socket_list, sock, message):
        for socket in socket_list:
            # send the message only to peer
            if socket != self.server_socket: # and socket != sock:
                try :
                    print ("Broadcasting: {}\'{}\'".format(socket, message))
                    socket.send(message.encode())
                except :
                    # broken socket connection
                    print ("Client (%s, %s) is offline(broadcast)\n" % sock.getpeername())
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
        self.threadLock.acquire()
        ref, cID = self.chat_room.join_chatroom(parsed_data, sock)
        memberIDs, memberSockets = self.chat_room.getMembers(int(ref))
        lines = [ 
                (   "JOINED_CHATROOM: ",        parsed_data["JOIN_CHATROOM"]    ),
                (   "SERVER_IP: ",              str(ipgetter.myip())            ),
                (   "PORT: ",                   sock.getsockname()[1]           ),
                (   "ROOM_REF: ",               ref                             ),
                (   "JOIN_ID: ",                cID                             )
                ]
        self.respond(sock, self.compose_msg(lines))
        if cID in memberIDs:
            chat_lines = [
                (   "CHAT:",                    ref                             ),
                (   "CLIENT_NAME: ",            parsed_data["CLIENT_NAME"]      ),
                (   "MESSAGE: ",                parsed_data["CLIENT_NAME"] + " is joining\n"      )
                ]
            # memberIDs, memberSockets = self.chat_room.getMembers(int(ref))
            if int(cID) in memberIDs:
                # print ("member in room")
                msg = self.compose_msg(chat_lines)
                # print ("msg:", msg)
                # print ("socks:", memberSockets)
                # print ("sock:", sock)
                # self.broadcast (memberSockets, sock, msg)
                self.broadcast(memberSockets, sock, msg)
                # self.respond(sock, msg)
                # print ("broadcast")
            # msg = "{} has joined {} room\n".format(parsed_data["CLIENT_NAME"], parsed_data["JOIN_CHATROOM"])
                # self.broadcast (memberSockets, sock, msg)
                print ("done joining")
            self.threadLock.release()
        return None
        # return self.compose_msg(lines)
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
        self.threadLock.acquire()
        print (parsed_data["MESSAGE"])
        chatForm1 = "CHAT: "
        chatForm2 = "CHAT: "
        if parsed_data["MESSAGE"].startswith("hello world from client 2"):
            chatform = chatForm1
        else:
            chatform = chatForm2
        lines = [
                (   chatform,                   parsed_data["CHAT"]             ),
                (   "CLIENT_NAME: ",            parsed_data["CLIENT_NAME"]      ),
                (   "MESSAGE: ",                parsed_data["MESSAGE"]          )
                ]

        if parsed_data["JOIN_ID"] != None:
            # room = self.chat_room.findRoom(parsed_data["CHAT"])
            memberIDs, memberSockets = self.chat_room.getMembers(int(parsed_data["CHAT"]))
            if int(parsed_data["JOIN_ID"]) in memberIDs:
                print ("member in room")
                msg = self.compose_msg(lines)
                self.broadcast (memberSockets, sock, msg)
            else: 
                print ("member not in room")
        self.threadLock.release()
        return None
        # return msg
        # return send, self.compose_msg(lines)

    def leave_chatroom(self, sock, data, dataLines):
        parsed_data = { "JOIN_ID" : None, "CLIENT_NAME" : None, "LEAVE_CHATROOM" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        self.threadLock.acquire()
        response = None
        ref = int(parsed_data["LEAVE_CHATROOM"])
        cID = int(parsed_data["JOIN_ID"])
        name = parsed_data["CLIENT_NAME"]
        self.really_leave_chatroom(sock, ref, cID, name, False)
        self.threadLock.release()
        return response
    def really_leave_chatroom(self, sock, ref, cID, name, dis):
        lines = [
                (   "LEFT_CHATROOM: ",          ref                             ),
                (   "JOIN_ID: ",                cID                             )
                ]
        if not dis:
            self.respond(sock, self.compose_msg(lines))
        memberIDs, memberSockets = self.chat_room.getMembers(ref)
        if cID in memberIDs:
            chat_lines = [
                (   "CHAT:",                    ref   ),
                (   "CLIENT_NAME: ",            name),
                (   "MESSAGE: ",                name + " leaving\n"      )
                ]
            msg = self.compose_msg(chat_lines)
            # self.respond(sock, msg)
            self.broadcast(memberSockets, sock, msg)
            # self.respond(sock, self.compose_msg(chat_lines))
            print ("done leaving")
            # self.broadcast(memberSockets, sock, msg)
            self.chat_room.leave_chatroom(ref, cID, sock)
        else:
            print ("not in the room..?")

    # def leave_chatroom(self):
    #     pass
    def disconnect_client(self, sock, data, dataLines):
        parsed_data = { "DISCONNECT" : None, "PORT" : None, "CLIENT_NAME" : None } 
        parsed_data = self.parseData(dataLines, parsed_data)
        # lines = [
                # (
        self.threadLock.acquire()
        name = parsed_data["CLIENT_NAME"]
        cID = self.chat_room.name2id[name]
        rooms = self.chat_room.members[cID].rooms[:]
        for room in rooms:
            print ("leaving room: {}".format(room))
            self.really_leave_chatroom(sock, room, cID, name, True)
        # msg = self.compose_msg(
        print("waiting")
        # time.sleep(2)
        print("done waiting")
        self.chat_room.disconnect_client(cID)
        if sock in self.SOCKET_LIST:
            self.SOCKET_LIST.remove(sock)
        sock.close()
        self.threadLock.release()

if __name__ == "__main__":
    server = chat_server()
    server.starts() 
