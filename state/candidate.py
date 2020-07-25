import time
import random
from ..state.state import State
from ..state.leader import Leader
from ..config import Config
from ..message import *


class Candidate(State):

    # Initialize the candidate
    def __init__(self, server=None):
        State.__init__(self, server)
        self.voteReceived = {self.server.id: 1}
        self.votedFor = self.server.id
        self.server.setElectionTimer()
        self.requestElection()

    def requestElection(self):
        candId = self.server.id
        term = self.server.curTerm
        data = {
            'lastLogIndex': self.server.lastLogIndex(),
            'lastLogTerm': self.server.lastLogTerm()
        }
        # Build the vote request message
        message = VoteRequest(candId, None, term, data)
        # Actual send the message
        self.server.publish_message(message)
        return

    def voteResponseHandler(self, message):

        # If the server current term less than message term, not correct
        if message.term > self.server.curTerm:
            return
        elif message.term == self.server.curTerm:
            if message.data['voteGranted']:
                # If received vote from sender, add the vote into voteReceived
                self.voteReceived[message.sender] = 1
            else:
                # If sender refuse vote for candidate, set sender to zero
                self.voteReceived[message.sender] = 0

        # TODO: Check if the candidate can be promoted to leader
        if type(self.server.state) == Candidate and 2 * sum(self.voteReceived.values()) > Config.NUMBER_TOTAL_SERVERS:
            # Now promote to leader
            print(self.server.id+" become leader"+'\ncurrent term is: '+str(self.server.curTerm)
                  + " vote detail: "+str(self.voteReceived))
            Leader(self.server)
        return
