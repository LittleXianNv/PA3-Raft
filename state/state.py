import time
import random

class State(object):

    def __init__(self,server = None):
        self.leaderId = None       # Follower can redirect clients to leader
        self.server = server       
        self.votedFor = None       # CandidateId that received vote in current term
        self.currentTerm = 0;
        if server:
            self.server.set_state(self)
    
    # Initialize and specify the server to live
    def set_server(self, server):
        self.server = server

    # Send the vote response msg 
    def sendVoteResponse(self, message, voteGranted):
        data = {"voteGranted": voteGranted}
        # Build the response message
        response = VoteResponse(self.server.id, message.sender, message.term, data)
        if voteGranted:
            print(response.sender + " vote " + response.receiver +' current term is '+str(self.server.currentTerm))
        else:
            print(response.sender+" refuse to vote " + response.receiver)
        self.server.publish_message(response)

    # Handle the vote request message
    def voteRequestHandler(self, message): 
        # If the message term is outdated, discard the message
        if message.term < self.server.currentTerm or "lastLogIndex" not in message.data.keys():
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
    def voteReponseHandler(self, message): 
        pass
        
    def appendEntryRequestHandler(self, message): 
        pass

    def appensEntryResponseHandler(self, message): 
        pass

    # Response to the sender that message received is not correct
    def sendBadResponse(self, message): 
        data = {}
        response = BadResponse(self.server.name, message.sender, message.term, data)
        self.server.send_response(response)

    # General message handler
    def handle_message(self, message):
        if message.type is None or message.term is None:
            self.sendBadResponse(message)
            return
        
        # TODO: Update the election timer

        # TODO: check the base message type and then handle
        if message.type == BaseMessage.APPEND_ENTRIES_REQUEST:
            self.appendEntryRequestHandler(message)
        elif message.type == BaseMessage.VOTE_REQUEST:
            self.voteRequestHandler(message)
        elif message.type == BaseMessage.APPEND_ENTRIES_RESPONSE:
            self.appensEntryResponseHandler(message)
        elif message.type == BaseMessage.VOTE_RESPONSE:
            self.voteReponseHandler(message)
        elif message.type == BaseMessage.BAD_RESPONSE:
        else:
            pass

    def handle_client_request(self, request):
        if self.leaderId:
            # TODO: reply it with ip and port message
        else:
            response = ServerResponse('500',{})
        return response