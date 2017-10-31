#!/usr/local/bin/python3

class chatRoom ():
    def __init__(self):
        self.num_rooms = 0
        self.num_clients = 0
        self.room2ref = {}
        self.ref2room = {}
        self.ref2id = {}
        self.id2ref = {}
        self.id2name = {}
        self.name2id = {}
        # self.roomLock = threading.Lock()
        # self.clientLock = threading.Lock()

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
