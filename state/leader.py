import time
import random
from ..state.state import State
from ..message import *
from ..config import Config
from collections import defaultdict
import threading

class Leader(State):
    def __init__(self,server=None):
        State.__init__(self,server)
        self.matchIndex = defaultdict(int)
        self.nextIndex = defaultdict(int)
        for adjacent in self.server.adjacents:
            # For each server, index of the next log entry to send to that server
            self.nextIndex[adjacent] = self.server.lastLogIndex() + 1
            # For each server, index of highest log entry known to be replicated on server
            self.matchIndex[adjacent] = 0
        if self.server.timer:
            self.server.timer.cancel()
        # heartbeat
        self.hThread = threading.Thread(target=self.heartbeat)
        self.hThread.start()

    def handle_vote_request(self, message):
    # Leader would refuse any vote request except the one contain higher term (leader would convert to follower)
        self.sendVoteResponse(message, False)

    def handle_append_entries_response(self, message):
        if message.data['success']:
            # Update the index 
            self.matchIndex[message.sender] = message.data['matchIndex']
            self.nextIndex[message.sender] = message.data['matchIndex'] + 1
            self.updateCommitIndex()
        else:
            print("Error: Receive false response from " + message.sender)
            # TODO: prevent false response to corrupt nextIndex

    def updateCommitIndex(self):
        machedIndexArray = sorted(self.matchIndex.values())
        # Find out the index to update
        for i, matchIndex in enumerate(machedIndexArray):
            if matchIndex > self.server.commitIndex:
                if len(machedIndexArray) - i >= (len(machedIndexArray) / 2):
                    # Update the commit index and log the commit index
                    self.server.commitIndex = matchIndex
                    self.server.applyLog(self.server.commitIndex)
                return

    def handle_client_request(self, request):
        if request.type == 'GET':
            key = request.payload['key']
            # TODO: Response the server
            
        elif request.type == 'PUT':
            self.server.log.append({'action':request.payload, 'term':self.server.curTerm})
            time.sleep(0.3) # Wait the log to be applied
            # Response the server
            index =self.server.lastLogIndex()
            if self.server.lastApplied >= index:
                return ServerResponse('200',{})
            else:
                return ServerResponse('400',{})
        return response

    # TODO: heartbeat
    def heartbeat(self):
        while True:
            if self.server.state == self: 
                # Specify heartbeart message to all adjacient nodes
                for adjacent in self.server.connectedNode:
                    self.server.log_lock.acquire()
                    data={
                    'prevLogIndex': self.server.lastLogIndex(),
                    'prevLogTerm': self.server.lastLogTerm(),
                    'entries': [],
                    'leaderCommit': self.server.commitIndex
                    }
                    self.server.logLock.release()

                    if self.server.lastLogIndex() >= self.nextIndex[adjacent]:
                        data['prevLogIndex']=self.nextIndex[adjacent]-1
                        data['prevLogTerm']=self.server.log[data['prevLogIndex']]['term']
                        data['entries']=self.server.log[self.nextIndex[adjacent]:self.server.lastLogIndex()+1]
                    message = AppendEntriesRequest(self.server.id, adjacent, self.server.curTerm, data)
                    self.server.publishMsg(message)
                time.sleep(0.2)
            else:
                return