#!/usr/local/bin/python3
# client.py
import socket
import sys
import select
class client():
    def __init__(self, ip, port, message, name):
        # print ("in init")
        self.name = name
        self.joinFirst(ip, port, message)
        # print ("finished joining")
        self.loop()

        # read_sockets, write_sockets, error_sockets = select.select([self.sock], [], [])
        # while 1:
        #     (conn, (IP, PORT)) = lsock.accept()
        #     response = conn.recv(1024).decode()
        #     print("Received: \n{}".format(response))

    def joinFirst(self, ip, port, message):
        print ("IP:", ip, type(ip))
        print ("Port:", port, type(port))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        parsed_data = self.joinChatroom(message)
        # print ("parsed:", parsed_data)
        # self.sock.close()
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = self.sock.getsockname()
        self.id = parsed_data["JOIN_ID"]
        self.ref = parsed_data["ROOM_REF"]
        # print (self.port)
        # self.port = int(parsed_data["PORT"])
        # print ("port", self.port)
        # try:
        #     self.sock.connect((self.ip, self.port))
        # except:
        #     print ("unable to connect")

    def joinChatroom(self, message):
        msg = self.join(message)
        print ("Sending: \n{}".format(msg))
        # self.sock.sendall(msg.encode())
        response = self.sock.recv(1024).decode()
        print("Received: \n{}".format(response))
        lines = self.parseLines(response)
        # print ("lines:", lines)
        parsed_data = { "JOINED_CHATROOM" : None, "SERVER_IP" : None, "PORT" : None,  "ROOM_REF" : None, "JOIN_ID" : None } 
        parsed_data = self.parseData(lines, parsed_data)
        return parsed_data

    def loop(self):
        sys.stdout.write('[{}] '.format(self.name)); sys.stdout.flush() 
        while 1:
            socket_list = [sys.stdin, self.sock]
            # Get the list sockets which are readable
            ready_to_read,ready_to_write,in_error = select.select(socket_list, [], [])
            for sock in ready_to_read:
                if sock == self.sock:
                    # incoming message from remote server, s
                    data = sock.recv(4096)
                    if not data :
                        print ('\nDisconnected from chat server')
                        sys.exit()
                    else :
                        #print data
                        sys.stdout.write("\rRecieved:\n" + data.decode())
                        sys.stdout.write('[{}] '.format(self.name)); sys.stdout.flush() 
                else:
                    # user entered a message
                    msg = sys.stdin.readline()
                    commands = msg.split()
                    # print ("command:", commands[0])
                    # print("len:", len(commands))

                    if commands[0].startswith("send"):
                        # print ("in send")
                        if len(commands) > 1:
                            # print ("past send if")
                            if len(commands) > 2:
                                self.send(commands[1], commands[2:])
                            else:
                                self.send(self.ref, commands[1:])

                    elif commands[0].startswith("join"):
                        # print ("in join")
                        if len(commands) > 1:
                            # print ("past join if")
                            self.join(commands[1])
                    elif commands[0].startswith("leave"):
                        # print ("in leave")
                        if len(commands) > 1:
                            # print ("past leave if")
                            self.leave(commands[1])
                    elif commands[0].startswith("term"):
                        # print ("in term")
                        if len(commands) > 1:
                            # print ("past term if")
                            self.term(commands[1])
                    elif commands[0].startswith("kill"):
                        # print ("in term")
                        # print ("past term if")
                        self.kill()
                    sys.stdout.write('[{}] '.format(self.name)); sys.stdout.flush() 

    def send(self, Room, message):
        mess = " ".join(message)
        msg = "\
CHAT: {}\n\
JOIN_ID: {}\n\
CLIENT_NAME: {}\n\
MESSAGE: {}\n".format(int(Room), self.id, self.name, mess)
        print ("Sending:\n{}".format(msg))
        self.sock.send(msg.encode())
        return msg

    def join(self, Room):
        msg = "\
JOIN_CHATROOM: {}\n\
CLIENT_IP: 0\n\
PORT: 0\n\
CLIENT_NAME: {}\n".format(Room, self.name)
        print ("Sending:\n{}".format(msg))
        self.sock.send(msg.encode())
        return msg

    def leave(self, Room):
        msg = "\
LEAVE_CHATROOM: {}\n\
JOIN_ID: {}\n\
CLIENT_NAME: {}\n".format(Room, self.id, self.name)
        # return msg
        print ("Sending:\n{}".format(msg))
        self.sock.send(msg.encode())
        return msg

    def kill(self):
        msg = "KILL_SERVICE\n"
        # return msg
        print ("Sending:\n{}".format(msg))
        self.sock.send(msg.encode())
        return msg
    def term(self):
        pass

    def parseLines(self, dataString):
        # print ("in parseLines")
        lineList = dataString.splitlines()
        # print ("done parseLines")
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
ip = "0.0.0.0"
if len(sys.argv) >= 3:
    port = int(sys.argv[1])
    user = str(sys.argv[2])
    if len(sys.argv) > 3:
        ip = str(sys.argv[3])

sys.exit(client(ip, port, "helloWorld", user))
