#!/usr/bin/python3

import json
import socket as socklib
import select
from threading import Thread
import time
import re


ACTIONS={}


class SocketServer():
    def __init__(self, addr):
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

        print("Serveur socket lancé (%s:%d)" % (self.addr[0], self.addr[1]))
    
    def send(self, socket, datas):
        datas =  {"datas": datas}
        print(datas)
        socket.send(json.dumps(datas).encode())
        

    def listen(self):
        while self.status:
            time.sleep(0.01)
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
                            reqlist = []
                            multi_req = re.search("(.*\})(\{.*)", rd)
                            while multi_req is not None:
                                group = multi_req.group(1)
                                reqlist.append(group)
                                rd = rd[len(group):len(rd)]
                                multi_req = re.search("(.*\})(\{.*)", rd)

                            reqlist.append(rd)

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
                                    func = ACTIONS[funccat][funcname]
                                    func(socket, funcargs)
                                else:
                                    for x in self.socketlist:
                                        self.send(x, req)       
            except KeyboardInterrupt:
                break
                    
def addActions(cat, funcname, func):
    global ACTIONS
    if cat not in ACTIONS:
        ACTIONS[cat] = {}

    ACTIONS[cat][funcname] = func



class CommandListener(Thread):
    def __init__(self, server):
        self.server = server
        Thread.__init__(self)

    def run(self):
        while self.server.status:
            try:
                msg = input("")
                if msg.startwith("/"):
                    if msg == "/exit":
                        for socket in self.server.socketlist:
                            socket.close()

                        self.server.status = False
            except:
                self.server.serversocket.close()
                print("Fermeture du chat..")
                break

