import time
import random

class State(object):

    def __init__(self,server=None):
        self.leaderId = None       # follower can redirect clients
        self.server = server       
        self.votedFor = None       # CandidateId that received vote in current term
        self.currentTerm = 0;
        if server:
            self.server.set_state(self)
    
    # Specify the server to live
    def set_server(self, server):
        self.server = server

    def sendVoteResponse(self, message, voteGranted):
        data = {"voteGranted": voteGranted}
        response = VoteResponse(self.server.id, message.sender, message.term, data)
        if voteGranted:
            print(response.sender + " vote " + response.receiver +' term is '+str(self.server.currentTerm))
        else:
            print(response.sender+" refuse to vote "+response.receiver)
        self.server.publish_message(response)

    def handle_vote_request(self,message):
        # TODO

    # NULL function for override
    def handle_vote_response(self,message):
        pass
        
    def handle_append_entries_request(self,message):
        pass

    def handle_append_entries_response(self, message):
        pass

    # General message handler
    def handle_message(self,message):
        if message.type is None or message.term is None:
            #self.send_bad_response(message)
            return
        
        #self.server.refresh_election_timer()
        # print(str(self.server.id+ ' receive ')+str(message.type))

        # TODO: check the base message type and then handle
        if message.type == BaseMessage.APPEND_ENTRIES_REQUEST:
            self.handle_append_entries_request(message)
        elif message.type == BaseMessage.VOTE_REQUEST:
            self.handle_vote_request(message)
        elif message.type == BaseMessage.APPEND_ENTRIES_RESPONSE:
            self.handle_append_entries_response(message)
        elif message.type == BaseMessage.VOTE_RESPONSE:
            self.handle_vote_response(message)
        elif message.type == BaseMessage.BAD_RESPONSE:
            print("ERROR! This message is bad. "+str(message))
        else:
            pass

    def handle_client_request(self, request):
        if self.leaderId:
            # TODO: reply it with ip and port message
        else:
            response = ServerResponse('500',{})
        return response