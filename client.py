import zmq
from ..config import Config
from message import *
from constants import *


class Client(object):
	argv = sys.argv
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

	def manageArgv(self):
		if argv[1]=='put':
			put(argv[2],argv[3])
		elif argv[1] == 'get':
			get(argv[2],argv[3])
		elif argv[1] == 'remove':
			remove(argv[2])
		elif argv[1] == 'ls':
			listing()
		elif argv[1] == 'locate':
			locate(argv[2])
		elif argv[1] == 'lshere':
			lshere()
		else:
			print("wrong input format!")
	

	def put(self,localfilename, fs533filename):
		# split localfile into file chunk
		chunk_num = 3
		chunk_list = [fs533filename+"."+i for i in range(chunk_num)]
		request = ServerRequest(PUT,{"filename":fs533filename,"file_chunks":chunk_list})
		response_data = self.sends(request)
		print(response_data)
		# TODO send file to the server indicated by response from leader
		response = self.sends(ServerRequest(PUT_DONE,{"filename":fs533filename,"file_chunks_ip":response_data}))
		print(response)

	def get(self, fs533filename, localfilename):
		request = ServerRequest(GET,{"filename":fs533filenames})
		response_data = self.sends(request)
		print(response_data)
		# TODO fetch data from follower
		# merge the chunk into file
	
	def remove(self, fs533filename):
		request = ServerRequest(REMOVE,{"filename":fs533filenames})
		print(response_data)
		# TODO request follower delete chunk
		response = self.sends(ServerRequest(REMOVE_DONE,{"filename":fs533filename}) # Ask leader to clean up metadata
		print(response)

	
	def listing_request(self):
		request = ServerRequest(LS,{})
		response = self.sends(request)
		print(response.data)
	

	def locate_request(self, fs533filename):
		request = ServerRequest(LOCATE,{"filename":fs533filename})
		response = self.sends(request)
		print(response.data)
	
	def lshere_request(self):
	
	def sends(request):
		socket=self.init_socket()
		socket.send_pyobj(request)
		try:
			response=socket.recv_pyobj()
			if response.code=='300':
				data=response.data
				self.ip=response.data["ip_address"]
				self.data=response.data["port"]
				socket.close()
				return self.sends(request)
			elif response.code=='200':
				print(request)
				print("succeeds")
				return response.data
			elif response.code=='400':
				print(request)
				print("fails")
				quit()
			elif response.code=='500':
				print("Server failed.")
				quit()
		except Exception as e:
			print(e)
		finally:
			socket.close()
