#!/usr/local/bin/python3

from clientServer import clientServer
import threading
import socket as sock
import select
import sys
# import Lock

class member ():
    def __init__(self, sock, name, cID):
        self.sock = sock
        self.name = name
        self.addr = sock.getsockname()
        self.cID = cID
        self.rooms = []

# class room (object):
class room ():
    def __init__(self, name, ref):
        self.name = name
        self.ref = ref
        self.members = []
    def __hash__(self):
        return self.ref
    def __cmp__(self, other):
        return (self.ref) == (other.ref)
    def __eq__(self, other):
        return (self.ref) == (other.ref)
    def __ne__(self, other):
        return not (self == other)

class chatRoom ():
    def __init__(self):
        self.num_rooms = 0
        self.num_clients = 0
        self.members = {}       # id->member
        self.rooms = {}         # room_ref->room
        self.name2room = {}     # room_name -> ref
        self.name2id = {} 
        # self.num_roomsLock = Lock()
        # self.num_membersLock = Lock()

    def join_chatroom(self, parsed_data, sock):
        # print ("in j_c in cr")
        ref = int(self.getRoom(parsed_data["JOIN_CHATROOM"]))
        cID = int(self.getClient(parsed_data["CLIENT_NAME"], sock))
        # print ("ref:", ref)
        # print ("cID", cID)
        if cID not in self.rooms[ref].members:
            print("member {} not in room {}".format(cID, ref))
            self.rooms[ref].members.append(cID)
        if ref not in self.members[cID].rooms:
            print("room {} not in member {}".format(ref, cID))
            self.members[cID].rooms.append(ref)
        return ref, cID

    def leave_chatroom(self, parsed_data, sock):
        ref = int(parsed_data["LEAVE_CHATROOM"])
        cID = int(parsed_data["JOIN_ID"])
        if ref in self.rooms and int(cID) in self.rooms[ref].members:
            print("room {} exists and member {} in it".format(ref, cID))
            self.rooms[ref].members.remove(cID)
        else:
            print ("r/m not exists")
            return 1
        if cID in self.members and ref in self.members[cID].rooms:
            print ("member {} exists and room {} in it".format(cID, ref))
            self.members[cID].rooms.remove(ref)
        else:
            print ("m/r not exists")
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
        if room_name in [ self.rooms[Room].name for Room in self.rooms ]:
            return self.name2room[room_name]
        else:
            return self.createRoom(room_name)
    def createRoom(self, room_name):
        # num_roomsLock.aquire() 
        try:
            num_rooms = self.num_rooms
            self.num_rooms += 1
        finally:
            pass
            # num_roomsLock.release()
        newRoom = room(room_name, num_rooms)
        self.rooms[newRoom.ref] = newRoom
        self.name2room[room_name] = newRoom.ref
        print ("created new room", self.rooms)
        return newRoom.ref

    def getClient(self, client_name, sock):
        if client_name in [ self.members[Member].name for Member in self.members ]:
            return self.name2id[client_name]
        else:
            return self.createClient(sock, client_name)
    def createClient(self, sock, client_name):
        # num_membersLock.aquire() 
        try:
            num_clients = self.num_clients
            self.num_clients += 1
        finally:
            pass
            # num_membersLock.realease() 
        newClient = member(sock, client_name, num_clients)
        self.members[newClient.cID] = newClient
        self.name2id[client_name] = newClient.cID
        return newClient.cID
    
    
    def getMembers(self, ref):
        # print ("current rooms:", self.rooms)
        if ref in self.rooms:
            # print ("ref is in it!")
            memberIDs = self.rooms[ref].members
            memberSockets = [ self.members[cID].sock for cID in memberIDs ] 
            return memberIDs, memberSockets
        else:
            return [], []
