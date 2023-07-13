from multiprocessing import Process
from subprocess import call
from time import sleep

def daemon():
    call(("python", "capture.py"))

def gui():
    call(("python", "main.py"))

Pdaemon = Process(target=daemon)
Pgui = Process(target=gui)

Pdaemon.start()
sleep(0.5)
Pgui.start()
Pgui.join()
Pdaemon.close()

