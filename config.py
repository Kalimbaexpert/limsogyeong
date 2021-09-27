from Server import Server, ServerInterfaceManager
from threading import Thread, active_count
import time

def cnter():
    while True: 
        print(active_count())
        time.sleep(1)

server = Server(ServerInterfaceManager)
server.Run()

asddass = Thread(target=cnter)
asddass.start()