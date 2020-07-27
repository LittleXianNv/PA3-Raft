from collections import deque
import random
import time
from threading import Timer
import threading
from metadata.metadata import Metadata
from state.candidate import Candidate
from state.follower import Follower
import zmq
from config import Config
from metadata.metadataManager import MetadataManager
import sys
sys.path.append("..")


class Server(object):

    # Server initialization, having three threads
    def __init__(self, id, state, log, connectedNode, initialTimeout=None):
        self.id = id
        self.state = state
        self.log = log
        self.connectedNode = connectedNode  # list of node id
        self.commitIndex = 0                # to count current term
        self.curTerm = 0
        self.lastApplied = -1
        self.state.setServer(self)
        print(self.id+" becomes follower")
        self.timer = None
        self.metadata = Metadata()
        self.metadataManager = MetadataManager(self.metadata, self.log, self)
        self.defaultTimeOut(initialTimeout)

        self.msgBuffer = deque()  # to do: thread safe design
        self.bufferLock = threading.RLock()
        self.logLock = threading.RLock()
        self.pThread = threading.Thread(target=self.publishTask)
        self.pThread.start()
        self.sThread = threading.Thread(target=self.subscribeTask)
        self.sThread.start()
        self.pThread = threading.Thread(target=self.processClient)
        self.pThread.start()

    # Thread, wait for client request and handle it
    def processClient(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://127.0.0.1:%s" % Config.SERVER_LIST[self.id][2])
        print("processing" + str(self.id))
        while True:
            # if the response is not python object, there will be an exception.
            # try:
            request = socket.recv_pyobj()
            response = self.state.handle_client_request(request)
            socket.send_pyobj(response)
            # except Exception as e:
            #     print(e)

    def defaultTimeOut(self, initialTimeout):
        if not initialTimeout:
            self.setElectionTimer()
        else:
            self.setElectionTimer(initialTimeout)

    # Randomized election timeout to accelerate resolving the split vote problem
    def setElectionTimer(self, timeout=random.randrange(200, 400)/1000):
        # cancel original timer to prevent duplicated candidate living on one server
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(timeout, self.changeStateToCandidate)
        # if timeout, server change to cnadidate to send election request
        self.timer.start()

    # change server state from follower to candidate
    def changeStateToCandidate(self):
        self.curTerm += 1
        print(self.id+" becomes candidate and start election. term number is " +
              str(self.curTerm))
        # timer would be set again when initialing the state object
        Candidate(self)
        # current thread would do election and becomes leader if possible

    def publishTask(self):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://0.0.0.0:%d" % Config.SERVER_LIST[self.id][1])
        while True:
            if self.msgBuffer:
                self.bufferLock.acquire()
                message = self.msgBuffer.popleft()
                self.bufferLock.release()
                socket.send_pyobj(message)
            time.sleep(0.01)

    # subscribe the publish port of all adjacent server
    def subscribeTask(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        for node in self.connectedNode:
            socket.connect("tcp://127.0.0.1:%d" %
                           Config.SERVER_LIST[node][1])

        while True:
            socket.setsockopt(zmq.SUBSCRIBE, ''.encode('utf-8'))
            msg = socket.recv_pyobj()
            if msg.receiver == self.id or msg.receiver == None:
                self.receiveMsg(msg)

    # push the message to the publish message queue
    def publishMsg(self, msg):
        self.bufferLock.acquire()
        self.msgBuffer.append(msg)
        self.bufferLock.release()
        return

    def receiveMsg(self, msg):
        # call the handleMsg method state
        if self.curTerm < msg.term:
            # convert to follower
            self.curTerm = msg.term
            Follower(self)
        self.state.handleMsg(msg)
        return

    def applyLog(self, newLastAppliedIndex):
        print("ID "+str(self.id) + "Commit log")
        # apply actions to log
        for i in range(self.lastApplied+1, newLastAppliedIndex+1):
            logEntry = self.log[i]
            if logEntry["functionName"] == "WRITE":
                self.metadataManager.write(
                    logEntry["filename"], logEntry["fileChunkListIP"])
            elif logEntry["functionName"] == "DELETE":
                self.metadataManager.delete(logEntry["filename"])
        self.lastApplied = newLastAppliedIndex
    
    # return the index of the last log entry
    def lastLogIndex(self):
        return len(self.log)-1

    # return the term of the last log entry
    def lastLogTerm(self):
        return -1 if len(self.log) == 0 else self.log[-1]["term"]

    def setState(self, state):
        self.state = state
        return
