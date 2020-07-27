import random
from collections import defaultdict
from copy import copy


class MetadataManager(object):
    # unique manager run by Leader
    def __init__(self, metadata, log, server):
        self.metadata = metadata
        self.log = log
        self.server = server

    def preprocessPutRequest(self, filename, fileChunkList):
        # return {chunkName:List<ip>}
        ret = defaultdict(list)
        for chunkName in fileChunkList:
            print("ChunkName is: "+str(chunkName))
            if self.metadata.existFile(filename) and chunkName in self.metadata.filechunks:
                ret[chunkName].extend(self.filechunks[chunkName])
            else:
                ret[chunkName].extend(self.assignDataNode())
        return ret

    def processRemoveRequest(self, filename):
        # locate the filechunks to be removed
        ret = defaultdict(list)
        fileChunkList = self.metadata.filelist[filename]
        for chunkName in fileChunkList:
            if chunkName in self.metadata.filechunks:
                ret[chunkName].extend(self.filechunks[chunkName])
        return ret

    def processGetRequest(self, filename):
        # locate filechunks to be returned
        ret = dict()
        if not self.metadata.existFile(filename):
            return None
        for file_chunk in self.metadata.filelist[filename]:
            ret[file_chunk] = self.metadata.filechunks[file_chunk]
        return ret

    def processPutDoneRequest(self, filename, fileChunkListIP):
        # add the file information to the log to be added
        self.server.log.append(
            {"functionName": "WRITE", "filename": filename, "fileChunkListIP": fileChunkListIP, 'term': self.server.curTerm})

    def processRemoveDoneRequest(self, filename):
        # add the information of the file to the log to be removed
        self.server.log.append(
            {"functionName": "DELETE", "filename": filename, 'term': self.server.curTerm})

    def processLocateRequest(self, filename):
        # locate the chunks and return the information
        ret = dict()
        if not self.metadata.existFile(filename):
            return None
        for file_chunk in self.metadata.filelist[filename]:
            ret[file_chunk] = self.metadata.filechunks[file_chunk]
        return ret

    def processLSReqeust(self):
        # return all the keys in metadata
        return [key for key in self.metadata.filelist]

    def write(self, filename, fileChunkListIP):
        # log commit phase
        self.metadata.filelist[filename] = [key for key in fileChunkListIP]
        for file_chunk in fileChunkListIP:
            self.metadata.filechunks[file_chunk] = fileChunkListIP[file_chunk]

    def delete(self, filename):
        # log commit phase
        if filename not in self.metadata.filelist:
            return
        chunk_list = self.metadata.filelist[filename]
        del self.metadata.filelist[filename]
        for chunk_name in chunk_list:
            if chunk_name in self.metadata.filechunks:
                del self.metadata.filechunks[chunk_name]

    def assignDataNode(self):
        # return three ip hosts for replica
        copied_list = copy(self.server.connectedNode)
        random.shuffle(copied_list)
        print("Shuffle is " + str(copied_list[:3]))
        return copied_list[:3]
