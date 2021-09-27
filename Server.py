import socket 
from threading import Thread, active_count
import time
import CommunicationConsts as Consts


class Server:
#private :
    class __ClientRefVars:
        def __init__(self):
            self.clientId = None
            self.isReceiverRunnable = True
            self.isIdRegistered = False
            self.clientSocket = None
            self.downloadingFilebuffer = None
            self.isSendable = False
            self.downloaderNums = {}
            self.clientType = None
            self.sysProcessingMode = 0
            self.uploadingFileName = None
            self.uploadingFileSize = None
            self.isUploadingFile = False
            self.isCompleteUploading = False

    __downloadingFilePath = "./videos/"
    __uploadingFilePath = "./analysisFiles/"
    __connectedClientsInfo = {}
    __HOST = Consts.HOST
    __PORT = Consts.PORT
    __serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    __isServerRunnable = True
    __InterfaceManager = None

    def __RunReceiver(self, clientSocket, clientAddress): 
        interfaceManager = self.__InterfaceManager()
        msgBuffer = ""
        clientRefVars = Server.__ClientRefVars()
        clientRefVars.clientSocket = clientSocket
        print('Connected by :', clientAddress[0], ':', clientAddress[1]) 

        while self.__isServerRunnable and clientRefVars.isReceiverRunnable: 
            try:
                if clientRefVars.isUploadingFile:
                    self.__Upload(clientRefVars)

                if clientRefVars.isCompleteUploading:
                    clientId, uploaderNum = self.__GetInfoFromNonMessengerIdId(clientRefVars.clientId)
                    self.__SendSysMsg(clientId, "rm,"+str(uploaderNum))
                    self.DisconnectClient(clientRefVars.clientId)

                msgBuffer += clientSocket.recv(Consts.SysConsts.RECEIVING_MSG_SIZE.value).decode()
                endIdx = msgBuffer.find('\0')
                decodedMsg = msgBuffer[:endIdx]
                msgBuffer = msgBuffer[endIdx+1:]

                if self.__IsSysMsg(decodedMsg):
                    self.__PalsingLaunchSysMsg(clientRefVars, decodedMsg)           
                    continue   

                interfaceFuncArgs = (decodedMsg, clientRefVars.clientId, self)
                interfaceFuncThread = Thread(target=interfaceManager.InterfaceFunc, args=interfaceFuncArgs)
                interfaceFuncThread.start()
            except socket.timeout:
                continue
            except ConnectionResetError:
                break

        print('Disconnected by ' + clientAddress[0],':',clientAddress[1])
        time.sleep(0.1)            
        del self.__connectedClientsInfo[clientRefVars.clientId]
        clientSocket.close()

    def __Upload(self, clientRefVars):
        self.__SendSysMsg(clientRefVars.clientId, "uploadable")
        with open(self.__uploadingFilePath+clientRefVars.uploadingFileName, "wb") as video:
            buffer = None
            Q = clientRefVars.uploadingFileSize//Consts.SysConsts.RECEIVING_FILE_SIZE.value
            R = clientRefVars.uploadingFileSize%Consts.SysConsts.RECEIVING_FILE_SIZE.value
            for i in range(Q):
                buffer = clientRefVars.clientSocket.recv(Consts.SysConsts.RECEIVING_FILE_SIZE.value)
                video.write(buffer)
            buffer = clientRefVars.clientSocket.recv(R)
            video.write(buffer)
            print("CLIENT> Done reading bytes..")
        clientRefVars.isUploadingFile = False
        clientRefVars.isCompleteUploading = True

    def __PalsingLaunchSysMsg(self, clientRefVars, sysMsg):
        sysMsgBuffer = self.__GetSysMsg(sysMsg)
        decodedMsg = None
        endIdx = sysMsgBuffer.find(',')
        while endIdx != -1:
            decodedMsg = sysMsgBuffer[:endIdx]
            sysMsgBuffer = sysMsgBuffer[endIdx+1:]
            self.__LaunchSysMsg(clientRefVars, decodedMsg)
            endIdx = sysMsgBuffer.find(',')

        decodedMsg = sysMsgBuffer
        self.__LaunchSysMsg(clientRefVars, decodedMsg)

    def __GetAvailableDownloaderNum(self, clientId):
        downloaderNums = self.__connectedClientsInfo[clientId].downloaderNums
        for i in range(100):
            if downloaderNums.get(i) == None:
                return i
        return -1

    def __AddDownloaderNum(self, clientId, downloaderNum, downloadingFileName):
        self.__connectedClientsInfo[clientId].downloaderNums[downloaderNum] = downloadingFileName

    def __DelDownloaderNum(self, clientId, downloaderNum):
        del self.__connectedClientsInfo[clientId].downloaderNums[downloaderNum]

    def __LaunchSysMsg(self, clientRefVars, sysMsg):
        if not clientRefVars.isIdRegistered:
            if self.__IsClientId(sysMsg):
                clientRefVars.clientId = self.__GetClientId(sysMsg)
                self.__Register(clientRefVars)
            else:
                print("is not registered")
                return

        print("sys ", clientRefVars.clientId, ":", sysMsg)

        if sysMsg == 'quit':
            self.__del__()
        elif sysMsg == 'break':
            if clientRefVars.clientType == "downloader":
                clientId, downloaderNum = self.__GetInfoFromNonMessengerIdId(clientRefVars.clientId)
                self.__DelDownloaderNum(clientId, downloaderNum)

            self.DisconnectClient(clientRefVars.clientId)
        elif sysMsg == "downloadable":
            self.__Upload2Client(clientRefVars.clientId)
        elif sysMsg == "communicable":
            clientId, downloaderNum = self.__GetInfoFromNonMessengerIdId(clientRefVars.clientId)

            downloadingFileName = self.__connectedClientsInfo[clientId].downloaderNums[downloaderNum]

            self.__OpenFile(clientRefVars.clientId, downloadingFileName)
            downloadingfileSize = self.__GetFileSize(clientRefVars.clientId)

            self.__SendSysMsg(clientRefVars.clientId, 'fileOpened,'+str(downloadingfileSize)+','+downloadingFileName)
        elif sysMsg == "uploading":
            clientRefVars.sysProcessingMode = 1
            return

        if clientRefVars.sysProcessingMode == 1:
            clientRefVars.sysProcessingMode = 2
            clientRefVars.uploadingFileSize = int(sysMsg)
        elif clientRefVars.sysProcessingMode == 2:
            clientRefVars.sysProcessingMode =0
            clientRefVars.uploadingFileName = sysMsg
            clientRefVars.isUploadingFile = True

    def __GetInfoFromNonMessengerIdId(self, nonMessengerId):
        endIdx = nonMessengerId.find('@')
        clientId = nonMessengerId[:endIdx]

        buffer = nonMessengerId[endIdx+1:]
        endIdx = buffer.find('@')
        nonMessengerNum = int(buffer[endIdx+1:])

        return clientId, nonMessengerNum


    def __GetClientType(self, clientId):
            endIdx = clientId.find('@')
            if endIdx == None:
                print("is not type")
                return False

            buffer = clientId[endIdx+1:]
            if buffer.startswith("downloader") :
                return "downloader"
            elif buffer.startswith("uploader") :
                return "uploader"
            else:
                return "messenger"

    def __IsClientId(self, decodedMsg):
        if len(decodedMsg) < 2:
            return False

        if decodedMsg[:1] != "@":
            return False

        if decodedMsg[-1:] != "@":
            return False

        return True

    def __GetClientId(self, decodedMsg):
        return decodedMsg[1:-1]

    def __GetSysMsg(self, sysMsg):
        return sysMsg[3:-3]

    def __IsSysMsg(self, decodedMsg):
        if len(decodedMsg) < 6:
            return False

        if decodedMsg[:3] != "@@@":
            return False

        if decodedMsg[-3:] != "@@@":
            return False

        return True

    def __SendSysMsg(self, clientId, sendingMsg):
        self.SendMsg(clientId, "@@@"+sendingMsg+"@@@")
        return

    def __Register(self, clientRefVars):
        self.__connectedClientsInfo[clientRefVars.clientId] = clientRefVars
        clientRefVars.isSendable = True
        clientRefVars.isIdRegistered = True
        clientRefVars.clientType = self.__GetClientType(clientRefVars.clientId)
        self.__SendSysMsg(clientRefVars.clientId, "registered")
        print(clientRefVars.clientId, "is registered")

    def __RunReceiverHandler(self):
        while self.__isServerRunnable: 
            try:
                clientSocket, clientAddress = self.__serverSocket.accept()
                clientSocket.settimeout(Consts.SysConsts.MAX_WAITING_TIME.value)

                receiverArgs = (clientSocket, clientAddress)
                receiverThread = Thread(target=self.__RunReceiver, args=receiverArgs)
                receiverThread.start()
            except socket.timeout:
                continue

    def __RunSender(self, clientSocket, sendingMsg):
        sendingMsg = sendingMsg+"\0"
        clientSocket.sendall(sendingMsg.encode())

    def __OpenFile(self, clientId, downloadingFileName):
        openedFile = open(self.__downloadingFilePath+downloadingFileName, "rb")
        self.__connectedClientsInfo[clientId].downloadingFilebuffer = openedFile.read()

    def __GetFileSize(self, clientId):
        clientRefVars = self.__connectedClientsInfo[clientId]
        if clientRefVars.downloadingFilebuffer == None:
            print("file is not opened")
            return -1

        return len(clientRefVars.downloadingFilebuffer)
        #sendingMsg = str(len(clientRefVars.downloadingFilebuffer))
        #self.__SendSysMsg(clientId, str(len(clientRefVars.downloadingFilebuffer)))

    def __Upload2Client(self, clientId):                 #exeption
        if not self.__isServerRunnable:
            print("server is not running")
            return

        clientRefVars = self.__connectedClientsInfo.get(clientId)
        if clientRefVars == None:
            print("client is not connecting")
            return

        if clientRefVars.downloadingFilebuffer == None:
            return

        clientRefVars.isSendable = False
        clientRefVars.clientSocket.sendall(clientRefVars.downloadingFilebuffer)
        clientRefVars.isSendable = True
        clientRefVars.downloadingFilebuffer = None

#public :
    def __init__(self, InterfaceManager):
        self.__InterfaceManager = InterfaceManager
        self.__serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__serverSocket.settimeout(Consts.SysConsts.MAX_WAITING_TIME.value)
        self.__serverSocket.bind((self.__HOST, self.__PORT)) 
        self.__serverSocket.listen() 
        print('server start')

    def __del__(self):
        print("server terminate")
        for clientId, clientInfo in self.__connectedClientsInfo.items():
            self.__SendSysMsg(clientId, "break")
            #del(self.__connectedClientsInfo[clientId])
        self.__isServerRunnable = False
        self.__serverSocket.close()

    def Run(self):
        communicateHandlerThread = Thread(target=self.__RunReceiverHandler)
        communicateHandlerThread.start()

    def SendMsg(self, clientId, sendingMsg):
        if not self.__isServerRunnable:
            print("server is not running")
            return

        clientRefVars = self.__connectedClientsInfo.get(clientId)
        if clientRefVars == None:
            print("client is not connecting")
            return

        if not clientRefVars.isSendable:
            print("is not sendable")
            return

        senderArgs = (clientRefVars.clientSocket, sendingMsg)
        senderThread = Thread(target=self.__RunSender, args=senderArgs)
        senderThread.start()

    def DisconnectClient(self, clientId):
        self.__SendSysMsg(clientId, "break")
        self.__connectedClientsInfo[clientId].isReceiverRunnable = False
        #del(self.__connectedClientsInfo[clientId])

    def SendFile(self, clientId, fileName):
        downloaderNum = self.__GetAvailableDownloaderNum(clientId)
        if downloaderNum == -1:
            print("too many downloader")
            return

        self.__AddDownloaderNum(clientId, downloaderNum, fileName)
        sendingMsg = "creatDownloader,"+str(downloaderNum)
        self.__SendSysMsg(clientId, sendingMsg)

from video_pose_detector_student import *
from compare_similar import*
class ServerInterfaceManager:
    def __init__(self):
        self.mode = 0

    def InterfaceFunc(self, decodedMsg, clientId, server):
        print(clientId, ":", decodedMsg)

        if decodedMsg == 'q':
            server.SendMsg(clientId, 'q')
        elif decodedMsg == 'b':
            server.SendMsg(clientId, 'b')
        elif decodedMsg == 'd':
            server.SendFile(clientId, "se.mp4")
        elif decodedMsg ==  'sended':
            PoseEstimateStudent("analysisFiles/output.mp4")
            time.sleep(0.1)
            value_similar = SimilarCompare()
            print(value_similar)
            server.SendMsg(clientId, str(int(value_similar)))
