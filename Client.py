import socket
from threading import Thread, active_count
import time
import CommunicationConsts as Consts
import MultiView

class Client:
#private :
    #shared
    __HOST = Consts.HOST
    __PORT = Consts.PORT
    __InterfaceManager = None

    def __RunReceiver(self):
        interfaceManager = self.__InterfaceManager()
        msgBuffer = ""
        while self._isRecieverRunnable: 
            try:
                msgBuffer += self._clientSocket.recv(Consts.SysConsts.RECEIVING_MSG_SIZE.value).decode()
                endIdx = msgBuffer.find('\0')
                decodedMsg = msgBuffer[:endIdx]
                msgBuffer = msgBuffer[endIdx+1:]

                if self._IsSysMsg(decodedMsg):
                    self._PalsingLaunchSysMsg(decodedMsg)           
                    continue   

                interfaceFuncArgs = (decodedMsg, self)
                interfaceFuncThread = Thread(target=interfaceManager.InterfaceFunction, args=interfaceFuncArgs)
                interfaceFuncThread.start()
            except socket.timeout:
                continue
        self.__del__()

    def __RunSender(self, sendingMsg):
        sendingMsg = sendingMsg+"\0"
        self._clientSocket.sendall(sendingMsg.encode())

    def __RunDownloader(self, downloaderNum):
        downloaderId = self.__clientId+"@downloader@"+downloaderNum
        downloader = Downloader(downloaderId, DownloaderInterfaceFunction, self)
        downloader.Run()

    def __RunUploader(self, uploadingFileName):
        uploaderNum = self.__GetAvailableUploaderNum()
        if uploaderNum == -1:
            print("too many uploader")
            return

        self.__AddUploaderNum(uploaderNum, uploadingFileName)

        uploaderId = self.__clientId+"@uploader@"+str(uploaderNum)
        uploader = Uploader(uploaderId, UploaderInterfaceFunction, self, uploadingFileName)
        uploader.Run()

    def __GetAvailableUploaderNum(self):
        for i in range(100):
            if self.__uploaderFileNames.get(i) == None:
                return i
        return -1

#protected :
    #shared
    _filePath = "./clientVideos/"

    def _LaunchSysMsg(self, sysMsg):
        print("sys ", sysMsg)

        if sysMsg == 'break':
            self.__del__()
            return
        elif sysMsg == 'registered':
            self._isIdRegistered = True
            return
        elif sysMsg == 'rm':
            self.__sysProcessingMode = 2
            return
        elif sysMsg == "creatDownloader":
            self.__sysProcessingMode = 1
            return

        if self.__sysProcessingMode == 1:
            self.__sysProcessingMode == 0
            downloaderArg = [sysMsg]
            downloaderThread = Thread(target=self.__RunDownloader, args=downloaderArg)
            downloaderThread.start()
            return
        elif self.__sysProcessingMode == 2:
            self.__sysProcessingMode == 0
            self.__DelUploaderNum(int(sysMsg))

    def _PalsingLaunchSysMsg(self, sysMsg):
        sysMsgBuffer = self._GetSysMsg(sysMsg)
        decodedMsg = None
        endIdx = sysMsgBuffer.find(',')
        while endIdx != -1:
            decodedMsg = sysMsgBuffer[:endIdx]
            sysMsgBuffer = sysMsgBuffer[endIdx+1:]
            self._LaunchSysMsg(decodedMsg)
            endIdx = sysMsgBuffer.find(',')

        decodedMsg = sysMsgBuffer
        self._LaunchSysMsg(decodedMsg)

    def _GetSysMsg(self, sysMsg):
        return sysMsg[3:-3]

    def _IsSysMsg(self, decodedMsg):
        if len(decodedMsg) < 6:
            return False

        if decodedMsg[:3] != "@@@":
            return False

        if decodedMsg[-3:] != "@@@":
            return False

        return True

    def _RegisterClientId(self, sendingMsg):
        self.SendMsg("@@@@"+sendingMsg+"@@@@")
        return

    def _SendSysMsg(self, sendingMsg):
        if not self._isIdRegistered:
            print("is not registered")
            return

        self.SendMsg("@@@"+sendingMsg+"@@@")
        return

    def __AddUploaderNum(self, uploaderNum, uploadingFileName):
        self.__uploaderFileNames[uploaderNum] = uploadingFileName

    def __DelUploaderNum(self, uploaderNum):
        del self.__uploaderFileNames[uploaderNum]

#public :
    def __init__(self, clientId, InterfaceManager):
        #shared
        self.__InterfaceManager = InterfaceManager

        #individual
        self.__uploaderFileNames = {}
        self.__sysProcessingMode = 0
        self.__clientId = clientId
        self
        self._isIdRegistered = False
        self._isRecieverRunnable = True
        self._clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 

        self._clientSocket.settimeout(Consts.SysConsts.MAX_WAITING_TIME.value)
        self._clientSocket.connect((self.__HOST, self.__PORT))
        self._RegisterClientId(clientId)

    def __del__(self):
        #print(self.__clientId, ": disconnected")
        self._isRecieverRunnable = False
        self._clientSocket.close()

    def Run(self):
        receiverHandlerThread = Thread(target=self.__RunReceiver)
        receiverHandlerThread.start()

    def SendMsg(self, sendingMsg):
        senderArg = [sendingMsg]
        senderThread = Thread(target=self.__RunSender, args=senderArg)
        senderThread.start()

    def QuitServer(self):
        self._SendSysMsg("quit")

    def DisconnectServer(self):
        self._SendSysMsg("break")

    def SendFile(self, uploadingFileName):
        uploaderArg = [uploadingFileName]
        uploaderThread = Thread(target=self.__RunUploader, args=uploaderArg)
        uploaderThread.start()

class Uploader(Client):
#private :
    def __RunReceiver(self):
        msgBuffer = ""
        while self._isRecieverRunnable: 
            try:
                msgBuffer += self._clientSocket.recv(Consts.SysConsts.RECEIVING_MSG_SIZE.value).decode()
                endIdx = msgBuffer.find('\0')
                decodedMsg = msgBuffer[:endIdx]
                msgBuffer = msgBuffer[endIdx+1:]

                if self._IsSysMsg(decodedMsg):
                    self._PalsingLaunchSysMsg(decodedMsg)           
                    continue   
            except socket.timeout:
                continue
        self.__del__()

    def __OpenFile(self):
        openedFile = open(self._filePath+self.__uploadingFileName, "rb")
        self.__uploadingFilebuffer = openedFile.read()

    def __GetFileSize(self):
        if self.__uploadingFilebuffer == None:
            print("file is not opened")
            return -1

        return len(self.__uploadingFilebuffer)
        #sendingMsg = str(len(clientRefVars.downloadingFilebuffer))
        #self.__SendSysMsg(clientId, str(len(clientRefVars.downloadingFilebuffer)))

    def __Upload2Server(self):                 #exeption
        self._clientSocket.sendall(self.__uploadingFilebuffer)
        self.__uploadingFilebuffer = None

        interfaceFuncArg = [self.__parentClient]
        interfaceFuncThread = Thread(target=self.__InterfaceFunction, args = interfaceFuncArg)
        interfaceFuncThread.start()

#protected :
    def _LaunchSysMsg(self, sysMsg):
        print("sys ", sysMsg)

        if sysMsg == 'break':
            self.__del__()
            return
        elif sysMsg == 'registered':
            self._isIdRegistered = True
            uploadingfileSize = self.__GetFileSize()
            self._SendSysMsg("uploading,"+str(uploadingfileSize)+","+self.__uploadingFileName)
            return
        elif sysMsg == "uploadable":
            self.__Upload2Server()
            return

#public :
    def __init__(self, clientId, InterfaceFunction, parentClient, uploadingFileName):
        #individual
        self.__parentClient = parentClient
        self.__uploadingFileName = uploadingFileName
        self.__isCompleteUploading = False
        self.__InterfaceFunction = InterfaceFunction
        self.__uploadingFilebuffer = None

        self.__OpenFile()
        Client.__init__(self, clientId, None)

    def Run(self):
        self.__RunReceiver()

class Downloader(Client):
#private :
    def __RunReceiver(self):
        msgBuffer = ""
        while self._isRecieverRunnable: 
            try:
                if self.__isDownloadingFile:
                    self.__Download()

                if self.__isCompleteDownloading:
                    interfaceFuncArgs = (self.__parentClient, self.__downloadingFileName)
                    interfaceFuncThread = Thread(target=self.__InterfaceFunction, args = interfaceFuncArgs)
                    interfaceFuncThread.start()
                    self.DisconnectServer()

                msgBuffer += self._clientSocket.recv(Consts.SysConsts.RECEIVING_MSG_SIZE.value).decode()
                endIdx = msgBuffer.find('\0')
                decodedMsg = msgBuffer[:endIdx]
                msgBuffer = msgBuffer[endIdx+1:]

                if self._IsSysMsg(decodedMsg):
                    self._PalsingLaunchSysMsg(decodedMsg)           
                    continue   
            except socket.timeout:
                continue
        self.__del__()

    def __Download(self):
        self._SendSysMsg("downloadable")
        with open(self._filePath+self.__downloadingFileName, "wb") as video:
            buffer = None
            Q = self.__downloadingFileSize//Consts.SysConsts.RECEIVING_FILE_SIZE.value
            R = self.__downloadingFileSize%Consts.SysConsts.RECEIVING_FILE_SIZE.value
            for i in range(Q):
                buffer = self._clientSocket.recv(Consts.SysConsts.RECEIVING_FILE_SIZE.value)
                video.write(buffer)
            buffer = self._clientSocket.recv(R)
            video.write(buffer)
            print("SERVER> Done reading bytes..")
        self.__isDownloadingFile = False
        self.__isCompleteDownloading = True

#protected :
    def _LaunchSysMsg(self, sysMsg):
        print("sys ", sysMsg)

        if sysMsg == 'break':
            self.__del__()
            return
        elif sysMsg == 'registered':
            self._isIdRegistered = True
            self._SendSysMsg("communicable")
            return
        elif sysMsg == 'fileOpened':
            self.__downloadingMode = 1
            return

        if self.__downloadingMode == 1:
            self.__downloadingMode = 2
            self.__downloadingFileSize = int(sysMsg)
        elif self.__downloadingMode == 2:
            self.__downloadingMode =0
            self.__downloadingFileName = sysMsg
            self.__isDownloadingFile = True

#public :
    def __init__(self, clientId, InterfaceFunction, parentClient):
        #individual
        self.__parentClient = parentClient
        self.__downloadingMode = 0
        self.__downloadingFileName = None
        self.__downloadingFileSize = None
        self.__isDownloadingFile = False
        self.__isCompleteDownloading = False
        self.__InterfaceFunction = InterfaceFunction

        Client.__init__(self, clientId, None)

    def Run(self):
        self.__RunReceiver()

import pyfirmata as pf


class ClientInterfaceManager:
    # def __init__(self):
    #     # self.ard = pf.Arduino('/dev/ttyACM0')
    #     # self.p9 = ard.get_pin('d:9:s')
    #     # self.pos = 90

    def InterfaceFunction(self, decodedMsg, client):
        print("server :", decodedMsg)

        if decodedMsg == 'q':
            client.QuitServer()
        elif decodedMsg == 'b':
            client.DisconnectServer()
        elif decodedMsg == 'lft':
            # self.pos = self.pos -3
            # if self.pos<0:
            #     self.pos = 0
            # self.p9.write(pos)
            print("go left")
            time.sleep(0.5)
        elif decodedMsg == 'rgt':
            # self.pos = self.pos +3
            # if self.pos>180:
            #     self.pos = 180
            # self.p9.write(pos)
            print("go right")
            time.sleep(0.5)

def DownloaderInterfaceFunction(parentClient, downloadingFileName):
    time.sleep(0.1)
    MultiView.MultiView(downloadingFileName)
    print("okssival")
    parentClient.SendFile("output.mp4")
    

def UploaderInterfaceFunction(parentClient):
    time.sleep(1)
    parentClient.SendMsg("sended")
    print("ok")
"""
time.sleep(0.1)
MultiView.MultiView()
print("ok")
global client
SendTemp(client, "output.mp4")
"""

client = Client("aa", ClientInterfaceManager)
client.Run()
#client2 = Client("bb", ClientInterfaceManager)
#client2.Run()
while True: 
    sendingMsg = input('Enter Message : ')
    sendingMsg = str(sendingMsg)
    if sendingMsg == 'u':
        client.SendFile("cl.mp4")
    if sendingMsg != "":
        print("aa :", sendingMsg)        
        client.SendMsg(sendingMsg)

    #sendingMsg = input('Enter Message : ')
    #sendingMsg = str(sendingMsg)
    #if sendingMsg != "":
    #    print("bb : ", sendingMsg)        
    #    client2.SendMsg(sendingMsg)
    print(active_count())
    time.sleep(0.1)