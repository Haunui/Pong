#!/usr/bin/python3 

import time
from threading import Thread

CD_PER_D1 = 0
CD_PER_D10 = 1
CD_PER_D100 = 2
CD_PER_D1000 = 3

# Countdown class
#   Execute function or method after {ms} (milliseconds)
class Countdown(Thread):
    # ms : time (in milliseconds) before executing the function or the method
    # ref : the reference of the function or method
    # args : arguments of the function or method
    def __init__(self, ms, ref, *args):
        self.ms = ms

        self.func = [ref]
        for arg in args:
            self.func.append(arg)

        self.per_ms_func = {0: [],1: [],2: [],3: []}
        Thread.__init__(self)

    def addPerMSFunc(self, per, ref, *args):
        self.per_ms_func[per].append([ref, *args])

    def run(self):
        while True:
            if self.ms > 0:
                time.sleep(0.01)
                if self.ms % 1000 == 0:
                    for f in self.per_ms_func[CD_PER_D1000]:
                        muted_arg = []
                        for i in range(1, len(f)):
                            muted_arg.append(f[i])
                            if isinstance(f[i], str):
                                if f[i].find("{CD_PER_D1000}") != -1:
                                    muted_arg[i - 1] = f[i].replace("{CD_PER_D1000}", str(int(self.ms / 1000)))

                        if len(muted_arg) > 0:
                            f[0](muted_arg)
                        else:
                            f[0]()
                
                if self.ms % 100:
                    for f in self.per_ms_func[CD_PER_D100]:
                        muted_arg = []
                        for i in range(1, len(f)):
                            muted_arg.append(f[i])
                            if isinstance(f[i], str):
                                if f[i].find("{CD_PER_D100}") != -1:
                                    muted_arg[i - 1] = f[i].replace("{CD_PER_D100}", str(int(self.ms / 100)))

                        if len(muted_arg) > 0:
                            f[0](muted_arg)
                        else:
                            f[0]()
                
                if self.ms % 10:
                    for f in self.per_ms_func[CD_PER_D10]:
                        muted_arg = []
                        for i in range(1, len(f)):
                            muted_arg.append(f[i])
                            if isinstance(f[i], str):
                                if f[i].find("{CD_PER_D10}") != -1:
                                    muted_arg[i - 1] = f[i].replace("{CD_PER_D10}", str(int(self.ms / 10)))

                        if len(muted_arg) > 0:
                            f[0](muted_arg)
                        else:
                            f[0]()
                
                if self.ms % 1:
                    for f in self.per_ms_func[CD_PER_D1]:
                        muted_arg = []
                        for i in range(1, len(f)):
                            muted_arg.append(f[i])
                            if isinstance(f[i], str):
                                if f[i].find("{CD_PER_D1}") != -1:
                                    muted_arg[i - 1] = f[i].replace("{CD_PER_D1}", str(int(self.ms / 1)))

                        if len(muted_arg) > 0:
                            f[0](muted_arg)
                        else:
                            f[0]()

                self.ms -= 10
            else:
                if len(self.func) > 1:
                    self.func[0](self.func[1])
                else: self.func[0]()
                break
