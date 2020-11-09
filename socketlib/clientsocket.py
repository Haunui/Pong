#/usr/bin/python3

import json
import os
import signal
import socket as socklib
import select
from threading import Thread


class SocketClient(Thread):
    def __init__(self, addr):
        self.status = 1
        self.id = -1
        self.addr = addr
    
    def start(self):
        self.socket = socklib.socket(socklib.AF_INET, socklib.SOCK_STREAM)
        self.socket.connect(self.addr)
        Thread.__init__(self)
        Thread.start(self)
        print("((connect))")

        self.send({"type": "auth"})

    def send(self, datas):
        datas =  {"id": self.id, "datas": datas}
        self.socket.send(json.dumps(datas).encode())
        print("((sending))")

    def run(self):
        while self.status:
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
                            datas = json.loads(r.decode())
                            if datas['datas']['type'] == "auth":
                                self.id = datas['datas']['value']
                                print("Connexion = true (id:%d)" % (self.id))
                                if datas['datas']['value'] == -1:
                                    print("Connexion = false")
                                    print("Fermeture du programme ...")
                                    time.sleep(5)
                                    sys.exit(1)
            except Exception as e:
                print(str(e))

