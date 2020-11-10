#!/usr/bin/python3

import json
import socket as socklib
import select
from threading import Thread
import time
import re


SERVER_ACTIONS={}


class SocketServer(Thread):
    def __init__(self, addr):
        self.delay = 10

        self.socketlist = []
        self.gsocketlist = []
        self.status = True
        self.addr = addr

        self.freeidlist = []
        self.idc = 0

    def start(self):
        self.serversocket = socklib.socket(socklib.AF_INET, socklib.SOCK_STREAM)
        self.serversocket.setsockopt(socklib.SOL_SOCKET, socklib.SO_REUSEADDR, 1)
        self.serversocket.bind(self.addr)
        self.serversocket.listen()
        self.gsocketlist.append(self.serversocket)

        Thread.__init__(self)
        Thread.start(self)

        print("Serveur socket lancé (%s:%d)" % (self.addr[0], self.addr[1]))
    
    def send(self, socket, datas):
        datas =  {"datas": datas}
        socket.send(json.dumps(datas).encode())
        
    def sendtoall(self, datas):
        for socket in self.socketlist:
            self.send(socket, datas)

    def sendexcept(self, target_socket, datas):
        for socket in self.socketlist:
            if socket != target_socket:
                self.send(socket, datas)

    def run(self):
        while self.status:
            time.sleep(self.delay / 1000)
            try:
                sockets,_,_ = select.select(self.gsocketlist, [], [])
                for sc in sockets:
                    if sc == self.serversocket:
                        if(self.status == False):
                            break

                        socket, addr = self.serversocket.accept()
                        self.gsocketlist.append(socket)
                        self.socketlist.append(socket)
                        print("Connexion entrante..")
                    else:
                        r = sc.recv(4096)
                        if r == b'':
                            self.gsocketlist.remove(sc)
                            self.socketlist.remove(sc)
                            sc.close()
                            print("Connection closed")
                        else:
                            rd = r.decode()
                            reqlist = packet_to_jsonlist(rd)
                            
                            for req in reqlist:
                                datas = json.loads(req)
                                if datas['datas']['type'] == "auth":
                                    self.send(socket, {"type": "auth", "value": self.idc})
                                    print("Client authentifié : {}".format(self.idc))
                                    self.idc += 1
                                elif datas['datas']['type'] == "custom":
                                    funccat = datas['datas']['value']['cat']
                                    funcname = datas['datas']['value']['func']
                                    funcargs = datas['datas']['value']['args']
                                    
                                    global SERVER_ACTIONS
                                    if funccat in SERVER_ACTIONS:
                                        func = SERVER_ACTIONS[funccat][funcname]
                                        func(socket, funcargs)
            except KeyboardInterrupt:
                break
                    
def addActions(cat, funcname, func):
    global SERVER_ACTIONS
    if cat not in SERVER_ACTIONS:
        SERVER_ACTIONS[cat] = {}

    SERVER_ACTIONS[cat][funcname] = func


def packet_to_jsonlist(s):
    jsonlist = []
    try:
        count = 0
        current = 0
        for i in range(0, len(s)):
            if s[i] == '{':
                count += 1
            elif s[i] == '}':
                count -= 1
                if count == 0:
                    jsonlist.append(s[current:i+1])
                    current = i + 1
    except Exception as e:
        print(str(e))

    return jsonlist
