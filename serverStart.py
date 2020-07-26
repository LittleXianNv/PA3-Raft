# Start server node and call server.py
from state.follower import Follower
from state.candidate import Candidate
from servernode.server import Server
import shlex
import subprocess
import threading
import time
import sys


serverList = []
serverId = [i for i in range(1, 6)]

threads = []


for i, id in enumerate(serverId):
    if i == 0:
        t = threading.Thread(target=serverList.append, args=(Server(str(id), Follower(
            None), [], [str(_) for _ in serverId[:i]+serverId[i+1:]], 0.2),))
        # connectedNode list contains all other nodes expect itself
        t.start()
    else:
        t = threading.Thread(target=serverList.append, args=(Server(
            str(id), Follower(None), [], [str(_) for _ in serverId[:i]+serverId[i+1:]]),))
        t.start()
    threads.append(t)

for thread in threads:
    thread.join()
