import time
import random
from state.state import State
from message import *
from config import Config
from collections import defaultdict
import threading
from constants import *
import sys
sys.path.append("..")


class Leader(State):
    def __init__(self, server=None):
        State.__init__(self, server)
        self.matchIndex = defaultdict(int)
        self.nextIndex = defaultdict(int)
        for node in self.server.connectedNode:
            # For each server, index of the next log entry to send to that server
            self.nextIndex[node] = self.server.lastLogIndex() + 1
            # For each server, index of highest log entry known to be replicated on server
            self.matchIndex[node] = 0
        if self.server.timer:
            self.server.timer.cancel()
        # heartbeat
        self.hThread = threading.Thread(target=self.heartbeat)
        self.hThread.start()

    def voteRequestHandler(self, message):
        # Leader would refuse any vote request except the one contain higher term (leader would convert to follower)
        self.sendVoteResponse(message, False)

    def appendEntryResponseHandler(self, message):
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
        print("Leader receiving " + request.type)
        if request.type == GET:
            filename = request.payload["filename"]
            response_data = self.server.metadataManager.processGetRequest(
                filename)
            response = ServerResponse(200, response_data)

        elif request.type == PUT:
            filename = request.payload["filename"]
            file_chunks = request.payload["file_chunks"]
            response_data = response_data = self.server.metadataManager.preprocessPutRequest(
                filename, file_chunks)
            response = ServerResponse(200, response_data)

        elif request.type == PUT_DONE:
            filename = request.payload["filename"]
            file_chunks_ip = request.payload["file_chunks_ip"]
            self.server.metadataManager.processPutDoneRequest(
                filename, file_chunks_ip)
            response = ServerResponse(200, {})

        elif request.type == REMOVE:
            filename = request.payload["filename"]
            response_data = self.server.metadataManager.processRemoveRequest(
                filename)
            response = ServerResponse(200, response_data)

        elif request.type == REMOVE_DONE:
            filename = request.payload["filename"]
            self.server.metadataManager.processRemoveDoneRequest(
                filename)
            response = ServerResponse(200, {})

        elif request.type == LOCATE:
            filename = request.payload["filename"]
            response_data = self.server.metadataManager.processLocateRequest(
                filename)
            response = ServerResponse(200, response_data)
        elif request.type == LS:
            response_data = self.server.metadataManager.processLSReqeust()
            response = ServerResponse(200, response_data)

        return response

    def heartbeat(self):
        while True:
            if self.server.state == self:
                # Specify heartbeart message to all adjacent nodes
                for node in self.server.connectedNode:
                    self.server.logLock.acquire()
                    data = {
                        'prevLogIndex': self.server.lastLogIndex(),
                        'prevLogTerm': self.server.lastLogTerm(),
                        'entries': [],
                        'leaderCommit': self.server.commitIndex
                    }
                    self.server.logLock.release()

                    if self.server.lastLogIndex() >= self.nextIndex[node]:
                        data['prevLogIndex'] = self.nextIndex[node]-1
                        data['prevLogTerm'] = self.server.log[data['prevLogIndex']]['term']
                        data['entries'] = self.server.log[self.nextIndex[node]
                            :self.server.lastLogIndex()+1]
                    message = AppendEntriesRequest(
                        self.server.id, node, self.server.curTerm, data)
                    self.server.publishMsg(message)
                time.sleep(0.2)
            else:
                return
