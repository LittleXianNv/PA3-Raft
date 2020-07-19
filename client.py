import zmq
from ..config import Config
from message import *


class Client(object):
    def __init__(self):
        # default
        self.id = 1
        self.ip = Config.NODE_LIST[str(self.id)][0]
        self.port = Config.NODE_LIST[str(self.id)][2]

    def init_socket(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://"+self.ip+":"+str(self.port))
        return socket

    def put(self, file_path):
        socket = self.init_socket()
