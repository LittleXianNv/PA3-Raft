import zmq
from config import Config
from message import *
from constants import *
import sys


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
        # split localfile into file chunk
        chunk_num = 3
        chunk_list = [fs533filename+"."+str(i for i in range(chunk_num))]
        request = ServerRequest(
            PUT, {"filename": fs533filename, "file_chunks": chunk_list})
        response_data = self.sends(request)
        print(response_data)
        # TODO send file to the server indicated by response from leader
        response = self.sends(ServerRequest(
            PUT_DONE, {"filename": fs533filename, "file_chunks_ip": response_data}))
        print(response)

    def get(self, fs533filename, localfilename):
        request = ServerRequest(GET, {"filename": fs533filename})
        response_data = self.sends(request)
        print(response_data)
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
        request = ServerRequest(LS, {})
        response = self.sends(request)
        print(response.data)

    def locate_request(self, fs533filename):
        request = ServerRequest(LOCATE, {"filename": fs533filename})
        response = self.sends(request)
        print(response.data)

    def lshere_request(self):
        pass

    def sends(self, request):
        socket = self.init_socket()
        socket.send_pyobj(request)
        try:
            response = socket.recv_pyobj()
            if response.code == '300':
                data = response.data
                self.ip = response.data["ip_address"]
                self.port = response.data["port"]
                print("Redirecting to"+self.ip+":"+str(self.port))
                socket.close()
                return self.sends(request)
            elif response.code == '200':
                print(response)
                print("succeeds")
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
