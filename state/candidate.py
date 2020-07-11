import time
import random
from ..state.state import State
from ..state.leader import Leader

class Candidate(State):

    # Initialize the candidate
    def __init__(self,server = None):
        State.__init__(self, server)
        self.voteReceived = {self.server.id: 1}
        self.votedFor = self.server.id
        #TODO: update the election timer
        self.requestElection()

    def requestElection(self):
        candId = self.server.id
        term = self.server.currentTerm
        data = {
            'lastLogIndex':self.server.lastLogIndex(),
            'lastLogTerm' :self.server.lastLogTerm()
        }
        # Build the vote request message
        message = VoteRequest(candId, None, term, data)
        # Actual send the message
        self.server.publish_message(message)
        return

    def voteResponseHandler(self, message):

        # If the server current term less than message term, not correct
        if message.term>self.server.currentTerm:
            return
        elif message.term == self.server.currentTerm:
            if message.data['voteGranted']:
                # If received vote from sender, add the vote into voteReceived
                self.voteReceived[message.sender] = 1
            else:
                # If sender refuse vote for candidate, set sender to zero 
                self.voteReceived[message.sender] = 0
        
        # TODO: Check if the candidate can be promoted to leader 
        
        return














        