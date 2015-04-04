import json, boto, uuid, time, base64, sys, getopt
from boto.sqs.message import RawMessage
import aws_commons, os
from os import walk, remove, stat
from os.path import join as joinpath

class Restore():
    _serverQueueName = 'server_queue'

    def __init__(self, **kwargs):
        self.clientQueueName = ''

    def createClientQueue(self, queueName, dirName):
        sqs = boto.connect_sqs()
        self.directory = dirName
        print('- This is the input directory for restore: %s' % self.directory)
        try:
            isDir = os.path.isdir(self.directory)
            if not isDir:
                print '- Invalid Dir. Enter correct one'
                sys.exit()
        except IOError:
            print '- IO Exception...Enter correct dir'
            sys.exit()
        sqs = boto.sqs.connect_to_region('us-west-1')
        queueExists = sqs.lookup(queueName)
        self.clientQueueName = queueName
        print('- Creating client queue... %s' % self.clientQueueName)
        input_var = ''
        if queueExists == None:
            q = sqs.create_queue(self.clientQueueName)
        self.sendMessageToServer()


    def sendMessageToServer(self):
        print '- Sending msg to Server for restore'
        data = {}
        data['restore'] = self.clientQueueName
        aws_commons.connectAndWriteToSQS(Restore._serverQueueName, data)



def main(argv):
    queueName = ''
    dirName = ''
    try:
        opts, args = getopt.getopt(argv,"hq:d:",["queueName="])
    except getopt.GetoptError:
        print 'restore.py -q <queueName>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'restore.py -q <queueName>'
            sys.exit()
        elif opt in ("-q", "--queueName"):
            queueName = arg
        elif opt in ("-d", "--dirName"):
            dirName = arg
    print '- Restore queue Name is "', queueName
    print '- Dir Name is "', dirName
    restore = Restore()
    restore.createClientQueue(queueName, dirName)
 

if __name__ == "__main__":
    main(sys.argv[1:]) 
