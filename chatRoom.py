#!/usr/local/bin/python3

from clientServer import clientServer
import threading
import socket as sock
import select
import sys
class chatRoom ():
    def __init__(self):
        self.num_rooms = 0
        self.num_clients = 0
        self.room2ref = {}
        self.ref2room = {}
        self.ref2id = {}
        self.id2server = {} 
        self.id2ref = {}
        self.id2name = {}
        self.name2id = {}
        # self.roomLock = threading.Lock()
        # self.clientLock = threading.Lock()

    def join_chatroom(self, parsed_data):
        print ("in j_c in cr")
        ref = self.getRoom(parsed_data["JOIN_CHATROOM"])
        cID = self.getClient(parsed_data["CLIENT_NAME"])
        print ("ref:", ref)
        print ("cID", cID)
        if self.add2room(ref, cID) == 0:
            print ("add2room == 0")
        return ref, cID

    def add2room(self, ref, cID):
        print ("ref:", ref)
        print ("cID:", cID)
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

    # def chat(self, ref, message):
    #     for key in self.ref2id:
    #         print (key, type(key))
    #     for member in self.ref2id[int(ref)]:
    #         server = self.id2server[member]
    #         socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    #         ip, port = server.server_address
    #         socket = server.socket
    #         socket.sendto(message.encode(), (ip, port))

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
    def createRoom(self, room_name):
        self.room2ref[room_name] = self.num_rooms
        self.ref2room[self.num_rooms] = room_name
        self.ref2id[self.num_rooms] = []
        self.num_rooms += 1
        return self.num_rooms - 1
    def findRoom(self, room_ref):
        if room_ref in self.ref2id:
            return self.ref2id[room_ref]
        else:
            return [None]

    def createClient(self, client_name):
        server, port = self.startServer()
        self.id2server[port] = server
        self.name2id[client_name] = port
        self.id2name[port] = client_name
        self.id2ref[port] = []
        self.num_clients += 1
        return port

    def getClient(self, client_name):
        if client_name in self.name2id:
            return self.name2id[client_name]
        else:
            return self.createClient(client_name)

    def startServer(self):
        HOST, PORT = "0.0.0.0", 0
        server = clientServer((HOST, PORT), self)
        # start a thread with the server. 
        server_thread = threading.Thread(target=server.loop)
        # exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        port = server.client_socket.getsockname()[1]
        return server, port
