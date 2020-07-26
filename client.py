import zmq
from config import Config
from message import *
from constants import *
import sys
from copy import deepcopy


class Client(object):
    def __init__(self):
        self.id = 2
        self.ip = Config.SERVER_LIST[str(self.id)][0]
        self.port = Config.SERVER_LIST[str(self.id)][2]

    def init_socket(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://"+self.ip+":"+str(self.port))
        return socket

    def manageArgv(self):
        argv = sys.argv
        if argv[1] == 'put':
            self.put(argv[2], argv[3])
        elif argv[1] == 'get':
            self.get(argv[2], argv[3])
        elif argv[1] == 'remove':
            self.remove(argv[2])
        elif argv[1] == 'ls':
            self.listing_request()
        elif argv[1] == 'locate':
            self.locate_request(argv[2])
        elif argv[1] == 'lshere':
            self.lshere_request()
        else:
            print("wrong input format!")

    def put(self, localfilename, fs533filename):
        # hardcode localfile into file chunk
        # TODO split file into chunks by specific size
        chunk_num = 3
        chunk_list = []
        for i in range(chunk_num):
            chunk_list.append(fs533filename+"."+str(int(i)))
        request = ServerRequest(
            PUT, {"filename": fs533filename, "file_chunks": chunk_list})
        response_data = self.sends(request)
        # TODO send file to the server indicated by response from leader
        response = self.sends(ServerRequest(
            PUT_DONE, {"filename": fs533filename, "file_chunks_ip": response_data}))

    def get(self, fs533filename, localfilename):
        response_data = self.locate_request(fs533filename)
        # call the locate function to search the file
        # TODO fetch data from follower
        # merge the chunk into file

    def remove(self, fs533filename):
        request = ServerRequest(REMOVE, {"filename": fs533filename})
        print(response_data)
        # TODO request follower delete chunk
        # Ask leader to clean up metadata
        response = self.sends(ServerRequest(
            REMOVE_DONE, {"filename": fs533filename}))
        print(response)

    def listing_request(self):
        # list all files in the file system
        request = ServerRequest(LS, {})
        response = self.sends(request)
        print(response)

    def locate_request(self, fs533filename):
        request = ServerRequest(LOCATE, {"filename": fs533filename})
        response = self.sends(request)
        # if the file is not found, print message
        if response == None:
            print("Not found")
            return None
        formated_response = deepcopy(response)
        # get the list where each chunk was stored
        for chunk_name in formated_response:
            formated_response[chunk_name] = [Config.SERVER_LIST[ID][0]+":"+str(Config.SERVER_LIST[ID][1])
                                             for ID in formated_response[chunk_name]]
        print(formated_response)
        return response

    def lshere_request(self):
        pass

    def sends(self, request):
        socket = self.init_socket()
        socket.send_pyobj(request)
        try:
            response = socket.recv_pyobj()
            print("Response type:" + str(response.code))
            if response.code == '300':
                data = response.data
                self.ip = response.data["ip_address"]
                self.port = response.data["port"]
                print("Redirecting to"+self.ip+":"+str(self.port))
                socket.close()
                return self.sends(request)
            elif response.code == '200':
                print(response)
                print("succeed")
                return response.data
            elif response.code == '400':
                print(response)
                print("fails")
                quit()
            elif response.code == '500':
                print("Server failed.")
                quit()
        except Exception as e:
            print(e)
        finally:
            socket.close()


client = Client()
client.manageArgv()
