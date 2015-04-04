import fileInfo

class Clientinfo():
    clientCount = 0
 #   fileNames = {} - use this for filename, hashvalue
    

##    def __init__(self, queueName, fileInfo):
##        self.queueName = queueName
##        self.fileInfo = fileInfo
##        ClientInfo.clientCount += 1

    def __init__(self, queueName):
        self.queueName = queueName
        ClientInfo.clientCount += 1

    def displayClientCount(self):
        print 'Total Num of clients %d' % ClientInfo.clientCount
