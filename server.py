#!/usr/bin/python3

import serversocket

def test(socket, args):
    print("Hello World")

def main():
    server = serversocket.SocketServer(("localhost", 7777))
    server.start()

    serversocket.addActions("test", "test", test)
    print(str(serversocket.ACTIONS))

    server.listen()


main()


