#/usr/bin/python3

import json
import socket as socklib
import select
from threading import Thread
import time
import re


CLIENT_ACTIONS={}


class SocketClient(Thread):
    def __init__(self, addr):
        self.delay = 10
        self.status = 1
        self.id = -1
        self.addr = addr
    
    def start(self):
        self.socket = socklib.socket(socklib.AF_INET, socklib.SOCK_STREAM)
        self.socket.connect(self.addr)
        Thread.__init__(self)
        Thread.start(self)
        # print("((connect))")

        self.send({"type": "auth"})

    def send(self, datas):
        datas =  {"id": self.id, "datas": datas}
        self.socket.send(json.dumps(datas).encode())
        # print("((sending))")

    def run(self):
        while self.status:
            time.sleep(self.delay / 1000)
            try:
                socks,_,_ = select.select([self.socket], [], [])
                for sock in socks:
                    if sock == self.socket:
                        if self.status == False:
                            break

                        r = self.socket.recv(4096)
                        if r == b'':
                            self.socket.close()
                            self.status = 0
                            print("[DEBUG] datas : %s" % (r))
                        else:
                            rd = r.decode()
                            reqlist = packet_to_jsonlist(rd)

                            for req in reqlist:
                                datas = json.loads(req)
                                if datas['datas']['type'] == "auth":
                                    self.id = datas['datas']['value']
                                    print("Connexion = true (id:%d)" % (self.id))
                                    if datas['datas']['value'] == -1:
                                        print("Connexion = false")
                                        print("Fermeture du programme ...")
                                        time.sleep(5)
                                        sys.exit(1)
                                elif datas['datas']['type'] == "custom":
                                    funccat = datas['datas']['value']['cat']
                                    funcname = datas['datas']['value']['func']
                                    funcargs = datas['datas']['value']['args']

                                    global CLIENT_ACTIONS
                                    if funccat in CLIENT_ACTIONS:
                                        func = CLIENT_ACTIONS[funccat][funcname]
                                        func(sock, funcargs)
            except KeyboardInterrupt:
                break

def addActions(cat, funcname, func):
    global CLIENT_ACTIONS
    if cat not in CLIENT_ACTIONS:
        CLIENT_ACTIONS[cat] = {}

    CLIENT_ACTIONS[cat][funcname] = func


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
