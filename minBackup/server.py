import json, boto, doWork, base64, time
import logging,sys
from boto.sqs.message import RawMessage
import aws_commons
import boto.sdb

class Server():
    timeCounter = 5
    

    def __init__(self, **kwargs):
        self.clientQueueName = ''
        self.clients = set()
        self.clientFileDict = {}

    def sendMessageToClient(self,clientName, fileName, fileHash):
        queueName = clientName
        data = {}
        data ={
            'fileName': fileName,
            'fileHash': fileHash
            }
        aws_commons.connectAndWriteToSQS(queueName, data)
        time.sleep(20)
   
    def storeMessageInSimpleDB(self, clientName, fileDict):
        # Item Name is file Hashvalue
        # Key is Clientname, Value is filename with abs path
        print '- In SimpleDB'
        simpleDB = boto.sdb.connect_to_region('us-west-1')
        domain = simpleDB.create_domain('minbackup-domain')
        item_attrs = {}        
        for key,value in fileDict.items():
            item_attrs[clientName] = key
            domain.put_attributes(value,item_attrs,False)
            print '- Storing file name and hashvalue: %s' % key
        print '\n'

    def updateSimpleDB(self, fileName, fileHash):
        print '- Received msg from Client that they are done. Updating SimpleDB with correct num of files for hashes....'
        simpleDB = boto.sdb.connect_to_region('us-west-1')
        domain = simpleDB.get_domain('minbackup-domain')
        if domain is not None:
            print domain
            item_name = fileHash
            item_attrs = {}
            item_attrs['minbackup.com'] = fileName
            domain.put_attributes(item_name, item_attrs, False)
        else:
            return
    print '\n'

    def dedup(self):
        unique = set()
        duplicates = []
        simpleDB = boto.sdb.connect_to_region('us-west-1')
        domain = simpleDB.lookup('minbackup-domain')
        if domain is None:
            return
        else:
            for hash in domain:
                retrievedItem = domain.get_item(hash.name)
                if len(retrievedItem) == 1:
                    print '- Asking client %s' % retrievedItem.keys()[0] ,'for file(s) %s' % retrievedItem.values()[0]
                    self.sendMessageToClient(retrievedItem.keys()[0], retrievedItem.values()[0], hash.name)
                    time.sleep(10)

    def querySimpleDB(self, clientName):
        simpleDB = boto.sdb.connect_to_region('us-west-1')
        data_dict = {}
        data = {}
        try:
            domain = simpleDB.get_domain('minbackup-domain')
            if domain is not None:
                for item in domain:
                    if clientName in item:
                        for key,value in item.items():
                            if clientName <> key:
                                data_dict[value] = key
            else:
                return
            print "- Files and directories to be fetched: %s " % data_dict
            print '\n'
            data['restore'] = data_dict
            print 'Length of dict %d' % len(data_dict)
            if len(data_dict) > 0:
                aws_commons.connectAndWriteToSQS(clientName, data)
            else:
                print 'No files found to send....'
                return
        except:
            print 'Exception occured while retrieving SimpleDB Domain....Either domain doesnt exist or no values in Domain'
            sys.exit()
            
    def restore(self, clientName):
        print '- Calculating files and dirs for restoring for client %s' % clientName
        self.querySimpleDB(clientName)
        

    def poll(self, wait=20, vtimeout=5):
        sqs = boto.connect_sqs()
        sqs = boto.sqs.connect_to_region('us-west-1')
        serverQ = sqs.get_queue('server_queue')
        clientName = ''
        fileDict = {}
        serverQ.set_message_class(RawMessage)
        while True:
            Server.timeCounter += 5
            print'- Server waiting to poll after %d seconds' % Server.timeCounter
            time.sleep(Server.timeCounter)
            m = serverQ.get_messages(10)
            if m:
                for result in m:
                    msg = json.loads(result.get_body())
                    clientName = msg.get('clientQueueName')
                    fileDict = msg.get('fileDict')
                    if msg.get('restore') is not None:
                        self.restore(msg.get('restore'))
                    # if client has uploaded file to S3,
                    # get uploaded filenames and update
                    # SimpleDB with filenames and hashes
                    elif msg.get('uploadedFileName') is not None and msg.get('uploadedFileHash') is not None:
                        self.updateSimpleDB(msg.get('uploadedFileName'), msg.get('uploadedFileHash'))
                    else:
                        print '- Received filenames with hashvalues from client %s' % clientName ,', will store in SimpleDB...'
                        self.storeMessageInSimpleDB(clientName,fileDict)
                    serverQ.delete_message(result)
            else:
                print('\n')
                print('- Calculating files reqd....')                
                if len(m) == 0:
                    self.dedup()
                    #iter = self.clients.__iter__()
                    #for s in iter:
                        #print(s)
                        #self.sendMessageToClient(s)
            self.poll()
                                                  
server = Server()
print('Server started....')
server.poll()
print('- Done writing to Client queue')
