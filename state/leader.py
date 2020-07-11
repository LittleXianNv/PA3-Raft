import time
import random
from ..state.state import State
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
        # TODO: heartbeat

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
                    self.server.apply_log(self.server.commitIndex)
                return

    def handle_client_request(self, request):
        if request.type == 'GET':
            key = request.payload['key']
            # TODO: Response the server
            
        elif request.type == 'PUT':
            self.server.log.append({'action':request.payload, 'term':self.server.currentTerm})
            time.sleep(0.3) # Wait the log to be applied
            # TODO: Response the server
        return response

    # TODO: heartbeat