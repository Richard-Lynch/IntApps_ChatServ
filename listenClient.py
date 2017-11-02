#!/usr/local/bin/python3
# client.py
import socket
import sys
import select
class client():
    def __init__(self, ip, port, message):
        print ("in init")
        self.joinFirst(ip, port, message)
        print ("finished joining")
        read_sockets, write_sockets, error_sockets = select.select([lsock], [], [])
        while 1:
            (conn, (IP, PORT)) = lsock.accept()
            response = conn.recv(1024).decode()
            print("Received: \n{}".format(response))

    def joinFirst(self, ip, port, message):
        print ("IP:", ip, type(ip))
        print ("Port:", port, type(port))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        parsed_data = self.joinChatroom(message)
        print ("parsed:", parsed_data)
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = int(parsed_data["PORT"])
        print ("port", self.port)
        try:
            self.sock.connect((self.ip, self.port))
        except:
            print ("unable to connect")

    def joinChatroom(self, message):
        print ("Sending: \n{}".format(message))
        self.sock.sendall(message.encode())
        response = self.sock.recv(1024).decode()
        print("Received: \n{}".format(response))
        lines = parseLines(response)
        print ("lines:", lines)
        parsed_data = { "CLIENT_IP" : None, "PORT" : None, "CLIENT_NAME" : None, "JOIN_CHATROOM" : None } 
        parsed_data = parseData(lines, parsed_data)
        return parsed_data

    def loop(self):
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
                        sys.stdout.write(data.decode())
                        sys.stdout.write('[Me] '); sys.stdout.flush() 
                else:
                    # user entered a message
                    msg = sys.stdin.readline()
                    commands = msg.split()
                    if commands[0].startswith("send"):
                        if len(commands) > 2:
                            self.send(commands[1], commands[1:])
                    elif commands[0].startswith("join"):
                        if len(commands) == 2:
                            self.join(commands[1])
                    elif commands[0].startswith("leave"):
                        if len(commands) == 2:
                            self.leave(commands[1])
                    elif commands[0].startswith("term"):
                        if len(commands) == 2:
                            self.term(commands[1]) 
                    sys.stdout.write('[Me] '); sys.stdout.flush() 

    def send(self, room, message):
        mess = "".join(message)
        msg = "\
        CHAT: 0\n\
        JOIN_ID: {}\n\
        CLIENT_NAME: Richie\n\
        MESSAGE: {}\n".format(self.port, mess)
        self.sock.send(msg.encode())

    def join(self, room):
        msg = "\
        JOIN_CHATROOM: {}\n\
        CLIENT_IP: 0\n\
        PORT: 0\n\
        CLIENT_NAME: Richie\n".format(room)
        self.sock.send(msg.encode())

    def leave(self, room):
        pass
    def term(self):
        pass

    def parseLines(self, dataString):
        print ("in parseLines")
        lineList = dataString.splitlines()
        print ("done parseLines")
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
port = int(sys.argv[1])
sys.exit(client("0.0.0.0", port, "helloWorld"))
