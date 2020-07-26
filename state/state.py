import time
import random
from message import *
from config import Config
import sys
sys.path.append("..")


class State(object):

    def __init__(self, server=None):
        self.leaderId = None       # Follower can redirect clients to leader
        self.server = server
        self.votedFor = None       # CandidateId that received vote in current term
        self.currentTerm = 0
        if server:
            self.server.setState(self)

    # Initialize and specify the server to live
    def setServer(self, server):
        self.server = server

    # Send the vote response msg
    def sendVoteResponse(self, message, voteGranted):
        data = {"voteGranted": voteGranted}
        # Build the response message
        response = VoteResponse(
            self.server.id, message.sender, message.term, data)
        if voteGranted:
            print(response.sender + " vote " + response.receiver +
                  ' current term is '+str(self.server.curTerm))
        else:
            print(response.sender+" refuse to vote " + response.receiver)
        self.server.publishMsg(response)

    # Handle the vote request message
    def voteRequestHandler(self, message):
        # If the message term is outdated, discard the message
        if message.term < self.server.curTerm or "lastLogIndex" not in message.data.keys():
            self.sendVoteResponse(message, False)

        elif (self.votedFor is None or self.votedFor == message.sender) and message.data["lastLogIndex"] >= (len(self.server.log) - 1):
            self.votedFor = message.sender
            if self.server.state == self:
                # Sender vote receiver
                self.sendVoteResponse(message, True)
            else:
                # Sender refuse to vote receiver
                self.sendVoteResponse(message, False)
        else:
            self.sendVoteResponse(message, False)

    # NULL function for override
    def voteResponseHandler(self, message):
        pass

    def appendEntryRequestHandler(self, message):
        pass

    def appendEntryResponseHandler(self, message):
        pass

    # Response to the sender that message received is not correct
    def sendBadResponse(self, message):
        data = {}
        response = BadResponse(
            self.server.name, message.sender, message.term, data)
        # self.server.send_response(response)

    # General message handler
    def handleMsg(self, msg):
        if msg.type is None or msg.term is None:
            self.sendBadResponse(msg)
            return

        # Update the election timer
        self.server.setElectionTimer()

        # Check the base message type and then handle
        if msg.type == Message.APPEND_ENTRIES_REQUEST:
            self.appendEntryRequestHandler(msg)
        elif msg.type == Message.VOTE_REQUEST:
            self.voteRequestHandler(msg)
        elif msg.type == Message.APPEND_ENTRIES_RESPONSE:
            self.appendEntryResponseHandler(msg)
        elif msg.type == Message.VOTE_RESPONSE:
            self.voteResponseHandler(msg)
        elif msg.type == Message.BAD_RESPONSE:
            print("ERROR")
        else:
            pass

    def handle_client_request(self, request):
        if self.leaderId:
            # reply it with ip and port message
            response = ServerResponse('300', {
                                      'ip_address': Config.SERVER_LIST[self.leaderId][0], 'port': Config.SERVER_LIST[self.leaderId][1], })
        else:
            response = ServerResponse('500', {})
        return response
