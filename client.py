#!/usr/bin/python3

import sys
from socketlib import clientsocket
from threading import Thread


def main():
    client = clientsocket.SocketClient(("localhost", 7777))
    client.start()

    client.send({'type': 'custom', 'value': {'cat': 'test', 'func': 'test', 'args': []}})

main()

