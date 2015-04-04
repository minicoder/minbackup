import json, boto, uuid, time, base64, sys, getopt
from uuid import getnode as get_mac
from os import walk, remove, stat
from os.path import join as joinpath
from boto.sqs.message import RawMessage
import glob, os, aws_commons
from datetime import datetime
from md5 import md5

class Client():
    _currentTime = ''
    _serverQueueName = ''

    def __init__(self, **kwargs):
        self.dirEntered = False
        self.directory = ''
        self.clientQueueName = ''
        Client._serverQueueName = 'server_queue'
        Client._currentTime = datetime.now().strftime('_%Y%m%d%H%M%S.')
    
    def connectToS3(self):
        s3 = boto.connect_s3()
        bucket = s3.create_bucket('message_pump.minbackup.com')
        key = bucket.new_key('examples/first_file.csv')
        key.set_contents_from_filename('/Users/swetha/ENV/minBackup/first_file.csv')

    def uploadFileToS3(self, fileName, fileHash):
        print '- Uploading files to S3...'
        s3 = boto.connect_s3()
        bucket = s3.create_bucket('minbackup.com')
        if type(fileName) is list:
            for f in fileName:
                split = f.split('.')
                if len(split) > 0:
                    fileWithTimestamp = Client._currentTime.join(split)
                    key = bucket.new_key(fileWithTimestamp)
                    key.set_contents_from_filename(f)
                break
        else:
            split = fileName.split('.')
            fileWithTimestamp = Client._currentTime.join(split)
            key = bucket.new_key(fileWithTimestamp)
            key.set_contents_from_filename(fileName)

        message = {}
        message['uploadedFileHash'] = fileHash
        message['uploadedFileName'] = fileWithTimestamp
        print '- Sending Message to Server that files are uploaded'
        aws_commons.connectAndWriteToSQS(Client._serverQueueName, message)
        
    def sendMessageToServer(self):
        isDir = False
        fileName = ''
        data = {}
        while True:
            file_list = []
            fileDict = dict()
            try:
                if not self.dirEntered:
                    print('- This is the input directory for backup: %s' % self.directory)
                    isDir = os.path.isdir(self.directory)
                    if not isDir:
                        print '- Invalid Dir. Enter correct one'
                        sys.exit()
                    if isDir:
                        self.dirEntered = True
                        for path, dirs, files in walk( self.directory ):
                            file_list.append(files)
                            for filename in files:
                                filepath = joinpath( path, filename )
                                with open(filepath) as openfile:
                                    fileHash = md5(openfile.read()).hexdigest()
                                fileDict[filepath] = fileHash
                        data ={
                            'clientQueueName': self.clientQueueName,
                            'fileDict': fileDict
                            }
                        print '- Data being sent to server: %s' % fileDict
                        aws_commons.connectAndWriteToSQS(Client._serverQueueName, data)
                else:
                    print('- Directory already enter...Using existing.. %s' % self.directory)
                    for path, dirs, files in walk( self.directory ):
                        file_list.append(files)
                        for filename in files:
                            filepath = joinpath( path, filename )
                            with open(filepath) as openfile:
                                fileHash = md5(openfile.read()).hexdigest()
                            fileDict[filepath] = fileHash
                        data ={
                            'clientQueueName': self.clientQueueName,
                            'fileDict': fileDict
                            }
                        print '- Data being sent to server: %s' % fileDict
                        aws_commons.connectAndWriteToSQS(Client._serverQueueName, data)
            except IOError:
                print '- IO Exception Enter correct one'
                sys.exit()
            except:
                print '- Invalid Value. Enter correct one'
                sys.exit()
            break
        self.poll()

    def poll(self, wait=20, vtimeout=5):
        sqs = boto.connect_sqs()
        sqs = boto.sqs.connect_to_region('us-west-1')
        print '\n'
        print('- Client Queue Polling will begin in 100 seconds for any new messages.... %s' % self.clientQueueName)
        q = sqs.get_queue(self.clientQueueName)
        q.set_message_class(RawMessage)
        while True:
            time.sleep(100)
            #print('Will wait for reply from server for 100 seconds....')
            m = q.get_messages(10)
            #print('Num of msgs in my queue: %d' % len(m))
            #if there are messages in client q, read them and delete msgs
            if m:
                for result in m:
                    msg = json.loads(result.get_body())
                    fileName = msg.get('fileName')
                    fileHash = msg.get('fileHash')
                    if msg.get('restore') is not None:
                        print '- Files and location of files for restore:'
                        print msg.get('restore')
                    elif fileName is not None and fileHash is not None:
                        print '- Received list of files that need to be uploaded to S3 from server'
                        self.uploadFileToS3(fileName, fileHash)
                    q.delete_message(result)
                    print '- Done...Messages deleted from queue'
                    print ('\n')
            else:
                if len(m) == 0:
                    print ('\n')
                    print('- Writing to Server Q since nothing to read....')
                    self.sendMessageToServer()
            self.poll()


    def createClientQueue(self, queueName, dirName):
        sqs = boto.connect_sqs()
        self.directory = dirName
        sqs = boto.sqs.connect_to_region('us-west-1')
        queueExists = sqs.lookup(queueName)
        self.clientQueueName = queueName
        print('- Creating client queue... %s' % self.clientQueueName)
        input_var = ''
        if queueExists == None:
            q = sqs.create_queue(self.clientQueueName)
        self.sendMessageToServer()
                
def main(argv):
    queueName = ''
    dirName = ''
    try:
        opts, args = getopt.getopt(argv,"hq:d:",["queueName="])
    except getopt.GetoptError:
        print 'client.py -q <queueName>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'client.py -q <queueName>'
            sys.exit()
        elif opt in ("-q", "--queueName"):
            queueName = arg
        elif opt in ("-d", "--dirName"):
            dirName = arg
    print '- Client queue Name is "', queueName
    print '- Dir Name is "', dirName
    client = Client()
    client.createClientQueue(queueName, dirName)
 

if __name__ == "__main__":
    main(sys.argv[1:]) 
