from enum import Enum, auto

HOST = '127.0.0.14'
PORT = 9999

class SysConsts(Enum):
    RECEIVING_MSG_SIZE = 1024
    RECEIVING_FILE_SIZE = 1024
    MAX_WAITING_TIME = 1
