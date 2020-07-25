# 5 servers can tolerate 2 failures
# create a server list here
class Config:
    NUMBER_TOTAL_SERVERS = 5
    SERVER_LIST = {
        # value :(ip,publish port, client socket)
        '1': ("127.0.0.1", 20001, 20006),
        '2': ("127.0.0.1", 20002, 20007),
        '3': ("127.0.0.1", 20003, 20008),
        '4': ("127.0.0.1", 20004, 20009),
        '5': ("127.0.0.1", 20005, 20010)
    }
