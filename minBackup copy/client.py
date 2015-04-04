import json, boto, uuid, time, base64, sys, getopt
from uuid import getnode as get_mac
from os import walk, remove, stat
from os.path import join as joinpath
from boto.sqs.message import RawMessage
import glob, os, aws_commons
from md5 import md5

class Client():
    _counter = 0

    def __init__(self, **kwargs):
        self.dirEntered = False
        self.directory = ''
        self.reply = ''
        self.userFileName = []
        self.clientQueueName = ''
        Client._counter += 1
 #       self.__class__._counter += 1

    
    def connectToS3(self):
        s3 = boto.connect_s3()
        bucket = s3.create_bucket('message_pump.minbackup.com')
        key = bucket.new_key('examples/first_file.csv')
        key.set_contents_from_filename('/Users/swetha/ENV/minBackup/first_file.csv')

    def uploadFileToS3(self, fileNames):
        s3 = boto.connect_s3()
        bucket = s3.create_bucket('minbackup.com')
        for fileName in fileNames:
            key = bucket.new_key(fileName)
            key.set_contents_from_filename(fileName)

    def sendMessageToServer(self, dirName):
        queueName = 'server_queue'
        print('In sendmsgtoserver client queue name is %s' % self.clientQueueName)
        isDir = False
        fileName = ''
        data = {}
        while True:
            file_list = []
            fileDict = dict()
            try:
                if not self.dirEntered:
  #                  self.reply = input('Enter directory:')
                    print('This is the input directory for backup: %s' % dirName)
 #                   self.directory = self.reply
                    isDir = os.path.isdir(dirName)
                    if not isDir:
                        print 'Invalid Dir. Enter correct one'
                        continue
                    if isDir:
                        self.dirEntered = True
                        #os.chdir(dirName)
                        #for files in glob.glob("*.*"):
                        for path, dirs, files in walk( dirName ):
                            file_list.append(files)
                        #for fileName in file_list:
                        for filename in files:
                            filepath = joinpath( path, filename )
                            with open(filepath) as openfile:
                                fileHash = md5(openfile.read()).hexdigest()
                            print 'Filepath %s' % filepath
                            print fileHash
                            fileDict[filepath] = fileHash
                            #fileDict.setdefault(fileName,[]).append(fileHash)
                        data ={
                            'clientQueueName': self.clientQueueName,
                            'fileDict': fileDict
                            }
                        aws_commons.connectAndWriteToSQS(queueName, data)

            # This else should never execute
                else:
                    print('Directory already enter...Using existing.. %s' % self.directory)
 #                   os.chdir(self.directory)
                    for files in glob.glob("*.*"):
                        file_list.append(files)
                        data ={
                            'fileName': file_list,
                            'clientQueueName':self.clientQueueName
                            }
                        aws_commons.connectAndWriteToSQS(queueName, data)

##                    for fName in file_list:
##                        fileName = fName
##                        print 'Writing file to Server queue %s' % fName
##                        data ={
##                            'fileName': fileName,
##                            'clientQueueName': self.clientQueueName
##                            }
##                        aws_commons.connectAndWriteToSQS(queueName, data)

            except IOError:
                print 'Invalid Dir...exception Enter correct one'
                continue
##            except:
##                print 'Invalid Value. Enter correct one'
##                continue
            break
        self.poll()



    def poll(self, wait=20, vtimeout=5):
        sqs = boto.connect_sqs()
        sqs = boto.sqs.connect_to_region('us-west-1')
        print('Polling after 1 min my client queue for any messages.... %s' % self.clientQueueName)
 #       time.sleep(60)
        q = sqs.get_queue(self.clientQueueName)
        q.set_message_class(RawMessage)
        while True:
            time.sleep(120)
            print('Waiting for server for 120 seconds....')
            m = q.get_messages(vtimeout)
            print('Num of msgs in my queue: %d' % len(m))
            #if there are messages in client q, read them and delete msgs
            if m:
                for result in m:
                    msg = json.loads(result.get_body())
                    print('MSG: %s' % msg.get('fileName'))
                    self.userFileName.append(msg.get('fileName'))
                    q.delete_message(result)
                    print 'filename: %s' % self.userFileName
                    if self.userFileName is not None:
                        #for fileName in self.userFileName:
#                            print fileName
                        self.uploadFileToS3(self.userFileName)
                    print 'Done...Msgs deleted'
                    
##            else:
##                print('Waiting for server for 60 seconds....')
##                time.sleep(60)
##                if len(m) == 0:
##                    print('Writing to Server Q since nothing to read....')
##                    self.sendMessageToServer()


    def createClientQueue(self, queueName, dirName):
        sqs = boto.connect_sqs()
        sqs = boto.sqs.connect_to_region('us-west-1')
        queueExists = sqs.lookup(queueName)
        self.clientQueueName = queueName
        print('Creating client queue... %s' % self.clientQueueName)
        input_var = ''
        if queueExists == None:
            q = sqs.create_queue(self.clientQueueName)
        self.sendMessageToServer(dirName)
                
def main(argv):
    queueName = ''
    dirName = ''
    try:
        opts, args = getopt.getopt(argv,"hq:d:",["queueName="])
    except getopt.GetoptError:
        print 'Client.py -q <queueName>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'Client.py -q <queueName>'
            sys.exit()
        elif opt in ("-q", "--queueName"):
            queueName = arg
        elif opt in ("-d", "--dirName"):
            dirName = arg
    print 'Client queue Name is "', queueName
    print 'Dir Name is "', dirName
    client = Client()
 #   clientInfo = clientInfo.Clientinfo(queueName)
#    clientInfo.displayClientCount()
 #   print 'Num of clients: %d' % Client._counter
    client.createClientQueue(queueName, dirName)
 

if __name__ == "__main__":
    main(sys.argv[1:]) 


#client = Client()
#print('Creating a client queue')
#client.createClientQueue()
#client.sendMessageToServer()
