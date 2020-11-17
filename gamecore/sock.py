from gamecore import core as m_core
from socketlib import serversocket, clientsocket

GAME__SOCKET_SERVER = 0
GAME__SOCKET_CLIENT = 1

class GameSocket:
    def __init__(self, core, status, addr):
        self.core = core

        self.status = status
        self.addr = addr
        
        if self.status == GAME__SOCKET_SERVER:
            self.sock = serversocket.SocketServer(self.addr)
            serversocket.addActions("game", "game", self.receive)
        elif self.status == GAME__SOCKET_CLIENT:
            self.sock = clientsocket.SocketClient(self.addr)
            clientsocket.addActions("game", "game", self.receive)

        self.sock.start()


    def send(self, socket, datas):
        datas = {'type': 'custom', 'value': {'cat': 'game', 'func': 'game', 'args': datas}}
        if self.status == GAME__SOCKET_CLIENT:
            self.sock.send(datas)
        else:
            if socket == None:
                self.sock.sendtoall(datas)
            else:
                self.sock.send(socket, datas)

    def sendexcept(self, socket, datas):
        datas = {'type': 'custom', 'value': {'cat': 'game', 'func': 'game', 'args': datas}}
        self.sock.sendexcept(socket, datas)

    def receive(self, socket, args):
        _type = args[0]

        if _type == "action":
            action = args[1]
            
            if self.core.status == m_core.GAME__STATUS_WAITING_FOR_PLAYER or self.core.status == m_core.GAME__STATUS_PRESTART or self.core.status == m_core.GAME__STATUS_START:
                if action == "prestart":
                    if self.status == GAME__SOCKET_CLIENT:
                        self.core.model.prestart(args[2])
                if action == "move":
                    entity = args[2]
                    ident = args[3]
                    x = args[4]
                    y = args[5]

                    if entity == "ball":
                        if self.status == GAME__SOCKET_CLIENT:
                            for ball in self.core.model.balls:
                                if ball.id == ident:
                                    ball.ball_coords.center = (x, y)
                                    break
                    elif entity == "player": 
                        for player in self.core.model.players:
                            if player.id == ident:
                                player.racket_coords.center = (x, y)
                                break
                
                    if self.status == GAME__SOCKET_SERVER:
                        self.sendexcept(socket, [_type, action, entity, ident, x, y])
       

        if self.core.status == m_core.GAME__STATUS_WAITING_FOR_PLAYER or self.core.status == m_core.GAME__STATUS_PRESTART or self.core.status == m_core.GAME__STATUS_START:
            if _type == "check":    
                check = args[1]
                if self.status == GAME__SOCKET_SERVER:
                    if check == "connect":
                        cdt = 5
                        self.core.model.prestart(cdt)
                        self.send(None, ['action', 'prestart',cdt])

                elif self.status == GAME__SOCKET_CLIENT:

                    if check == "updatescore":
                        team = args[2]
                        self.core.model.score[team] += 1
                        self.core.model.updateScore()

            elif _type == "config":
                if self.status == GAME__SOCKET_CLIENT:
                    config = args[1]
                    if config == "delay":
                        self.core.delay = args[2]
