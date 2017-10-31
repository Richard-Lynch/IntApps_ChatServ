#!/usr/local/bin/python3
import sys
from server import *
from client import client
from time import sleep

# print ("This is the name of the script: ", sys.argv[0])
# print ("Number of arguments: ", len(sys.argv))
# print ("The arguments are: " , str(sys.argv))


if __name__ == "__main__":
    # port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 0
    if len(sys.argv) > 1:
        print ("The port number to use is: ", sys.argv[1])
        PORT = int ( sys.argv[1] ) 

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    print ( "Port:", port, type(port))
    print ( "IP:", ip, type(ip))
    

    # start a thread with the server. 
    # the thread will then start one more thread for each request.
    server_thread = threading.Thread(target=server.serve_forever)

    # exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)
    stopServer = False
    # sleep(1000)
    while not stopServer:
        pass

    # client(ip, port, "Hello World 1")
    # client(ip, port, "Hello World 2")
    # client(ip, port, "Hello World 3")
    # client(ip, port, "HELO text\n")
    # client(ip, port, "KILL_SERVICE\n")

    # server.shutdown()
