class Message(object):
    '''

    This class is a wrapper class of necessary information. It is the subclass of the following four messages.
    And it contains four kinds of constant variables to indicate the type of messages. 

    Attributes:
            sender: A string, which represents the message's sender.
            receiver: A string, which represents the message's receiver.
            term: An integer, which represents the message's term.
            data: An dictionary, which contains other information. 
    '''
    APPEND_ENTRIES_REQUEST = 1
    APPEND_ENTRIES_RESPONSE = 2
    VOTE_REQUEST = 3
    VOTE_RESPONSE = 4
    BAD_RESPONSE = 5

    def __init__(self, sender, receiver, term, data):
        self.sender = sender
        self.receiver = receiver
        self.term = term
        self.data = data


class AppendEntriesRequest(Message):

    '''Append entries request

    This class represents the request to append entries.

    Attributes:
            sender, receiver, term: Please see above explainations.
            data: {
                    "leaderId": an integer to let follower redirect clients.
                    "prevLogIndex": an integer, index of log entry immediately preceding new ones.
                    "prevLogTerm": an integer, term of prevLogIndex entry
                    "entries": a list, log entries to store (empty for heartbeat; may send more than one for efficiency)
                    "leaderCommit": an integer, leader’s commit index
                    }
    '''

    def __init__(self, sender, receiver, term, data):

        Message.__init__(self, sender, receiver, term, data)
        self.type = Message.APPEND_ENTRIES_REQUEST


class AppendEntriesResponse(Message):

    '''Append entries response

    This class represents the response to append entries.

    Attributes:
            sender, receiver, term: Please see above explainations.
            data: {
                    "success": a boolean, true if follower contained entry matching prevLogIndex and prevLogTerm.
            }
    '''

    def __init__(self, sender, receiver, term, data):

        Message.__init__(self, sender, receiver, term, data)
        self.type = Message.APPEND_ENTRIES_RESPONSE


class VoteRequest(Message):

    '''Vote request

    This class represents the request to append entries.

    Attributes:
            sender, receiver, term: Please see above explainations.
            data: {
                    "candidateId": an integer, candidate requesting vote.
                    "lastLogIndex": an integer, index of candidate’s last log entry.
                    "lastLogTerm": an integer, term of candidate’s last log entry.
            }
    '''

    def __init__(self, sender, receiver, term, data):

        Message.__init__(self, sender, receiver, term, data)
        self.type = Message.VOTE_REQUEST


class VoteResponse(Message):

    '''Vote response

    This class represents the response to vote.

    Attributes:
            sender, receiver, term: Please see above explainations.
            data: {
                    "voteGranted": a boolean, true means candidate received vote.
            }
    '''

    def __init__(self, sender, receiver, term, data):

        Message.__init__(self, sender, receiver, term, data)
        self.type = Message.VOTE_RESPONSE


class BadResponse(Message):
    def __init__(self, sender, receiver, term, data):
        Message.__init__(self, sender, receiver, term, data)
        self.type = Message.BAD_RESPONSE


class ServerRequest(object):
    '''ServerRequest

    This class represents the request to server.

    Attributes:
            type: PREP_PUT|GET|PUT|PUT_DONE|LS|REMOVE_PREP|REMOVE|REMOVE_DONE|LOCATE|LSHERE
            payload: {
                    PREP_PUT:
                    "filename":String
                    -----------
                    GET:
                    "filename":String
                    -----------
                    PUT:
                    "filename":String
                    -----------
                    PUT_DONE:
                    "filename":String
                    -----------
            }
   '''

    def __init__(self, type, payload):
        self.type = type
        self.payload = payload


class ServerResponse(object):
    '''ServerResponse

    This class represents the response to client.

    Attributes:
            code : 200|300|400|500 (ok|redirect|bad|leader not found)
            data:{
                    if 200:
                            'value':Object(if request is GET)
                    if 300:
                            'ip_address':string,
                            'port':int
                    if 400:
                            None
            }
    '''

    def __init__(self, code, data):
        self.code = code
        self.data = data
