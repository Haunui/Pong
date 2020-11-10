#!/usr/bin/python3

from socketlib import serversocket
from threading import Thread
import time


def test(socket, args):
    print("Hello World")

def main():
    server = serversocket.SocketServer(("localhost", 7777))

    serversocket.addActions("test", "test", test)
    print(str(serversocket.ACTIONS))

    server.start()

