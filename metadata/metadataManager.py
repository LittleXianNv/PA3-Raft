import copy from copy
import random
import defaultdict from collections


class FileManager(object):
    # unique manager run by Leader
    def __init__(self, metadata, log, server):
        self.metadata = metadata
        self.log = log
        self.server = server

    def preprocessPutRequest(self, filename, fileChunkList):
        # return {chunkName:List<ip>}
        ret = defaultdict(list)
        for chunkName in fileChunkList:
            if self.metadata.existFile(filename) and chunkName in self.metadata.filechunks:
                ret[chunkName].extend(self.filechunks[chunkName])
            else:
                ret[chunkName].extend(self.assignDataNode())
        return ret

    def processGetRequest(self, filename):
        ret = dict()
        if filename not in self.metadata.existFile(filename):
            return None
        for file_chunk in self.metadata.filelist[filename]:
            ret[file_chunk] = self.metadata.filechunks[file_chunk]
        return ret

    def assignDataNode(self):
        # return three ip hosts for replica
        randomed_list = random.shuffle(self.server.connectedNodes)
        return randomed_list[:3]
