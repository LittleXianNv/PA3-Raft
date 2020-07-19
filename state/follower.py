import time
import random
from ..state.state import State
from ..message import *
from ..state.state import State
from ..config import Config

class Follower(State):

	def __init__(self,server = None):
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
		response = AppendEntriesResponse(self.server.id, message.sender, message.term, data)
		# Actually send the response message
		self.server.publishMsg(response)

	# handle the "appendEntryRequest" message
	def appendEntryRequestHandler(self, message):
		self.server.setElectionTimer()

		# If message term less than server current term, discard the msg
		if message.term < self.server.curTerm:
			self.sendAppendEntryResponse(message, False, self.server.lastLogIndex())
			return

		# If the message is empty, discard the message
		if message.data is None or message.data == {}:
			self.sendAppendEntryResponse(message, False, self.server.lastLogIndex())
			return
		else:
			log = self.server.log
			data = message.data

			#TODO: check the leader commit and previous log index
			# and send the sendAppendEntryResponse