# Start server node and call server.py
from servernode import erver
from state.follower import Follower
from state.candidate import Candidate
import shlex, subprocess
import threading
import time
import sys


serverList=[]
serverId = [i for i in range(1,6)]

threads=[]


for i,id in enumerate(ids):
    if i==0:
        t=threading.Thread(target=serverList.append,args=(Server(str(id),Follower(None), [],[str(_) for _ in serverId[:i]+serverId[i+1:]],0.2),))
        t.start()
    else:
        t=threading.Thread(target=serverList.append,args=(Server(str(id), Follower(None),[], [str(_) for _ in serverId[:i]+serverId[i+1:]]),))
        t.start()
    threads.append(t)

for thread in threads:
    thread.join()