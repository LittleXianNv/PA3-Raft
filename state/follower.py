import time
import random
from state.state import State
from message import *
from config import Config
import sys
sys.path.append("..")


class Follower(State):

    def __init__(self, server=None):
        # Initialize the server first
        State.__init__(self, server)
        if self.server:
            self.server.setElectionTimer()

    # Send the reponse of AppendEntry message
    def sendAppendEntryResponse(self, message, success, matchIndex):
        data = {"success": success}
        if success == True:
            # Update the match index
            data["matchIndex"] = matchIndex
        # Build the appendEntries response message
        response = AppendEntriesResponse(
            self.server.id, message.sender, message.term, data)
        # Actually send the response message
        self.server.publishMsg(response)

    # handle the "appendEntryRequest" message
    def appendEntryRequestHandler(self, message):
        self.server.setElectionTimer()

        # If message term less than server current term, discard the msg
        if message.term < self.server.curTerm:
            self.sendAppendEntryResponse(
                message, False, self.server.lastLogIndex())
            return

        # If the message is empty, discard the message
        if message.data is None or message.data == {}:
            self.sendAppendEntryResponse(
                message, False, self.server.lastLogIndex())
            return

        # and send the sendAppendEntryResponse
        else:
            log = self.server.log
            data = message.data

            if "leaderCommit" not in data.keys() or "prevLogIndex" not in data.keys() or "prevLogTerm" not in data.keys():
                self.sendAppendEntryResponse(
                    message, False, self.server.lastLogIndex())
                return
            else:
                # index is from 1, so here is <=
                if len(log) <= data["prevLogIndex"]:
                    self.sendAppendEntryResponse(
                        message, False, self.server.lastLogIndex())
                    return

                if len(log) > 0 and log[data["prevLogIndex"]]["term"] != data["prevLogTerm"]:
                    # delete the existing entry and all that follow it
                    self.server.log = log[0:data["prevLogIndex"]]
                    self.sendAppendEntryResponse(
                        message, False, self.server.lastLogIndex())
                    return
                else:
                    # keep entries from 0 to prevLogIndex
                    log = log[0:data["prevLogIndex"]+1]
                    for x in data["entries"]:
                        log.append(x)
                    self.server.log = log
                    if data["leaderCommit"] > self.server.commitIndex:
                        self.server.applyLog(self.server.commitIndex)
                        self.server.commitIndex = min(
                            data["leaderCommit"], self.server.lastLogIndex()+1)
                    self.leaderId = message.sender
                    self.sendAppendEntryResponse(
                        message, True, self.server.lastLogIndex())
