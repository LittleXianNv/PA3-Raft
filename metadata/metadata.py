from collections import defaultdict


class Metadata(object):
    def __init__(self):
        # map of file chunk to list of store ip
        self.filechunks = defaultdict(list)
        self.filelist = defaultdict(list)  # map of file and file chunk list

    def putFileChunk(self, fileChunkName, ip_list):
        # {
        # function:"put_file_chunk",
        # arguementlist:[["test_trunk1,..."],"test"]
        # }
        self.filechunks[fileChunkName] = ip_list

    def deleteFileChunk(self, fileChunkName):
        # Clean metadata for certain chunk
        del self.filechunks[fileChunkName]

    def getFileChunkStore(self, fileChunkName):
        # return list of ip which store the chunk
        return self.filechunks[fileChunkName]

    def existFile(self, filename):
        return filename in self.filelist

    def existFileChunk(self, fileChunkName):
        return fileChunkName in self.filechunks
