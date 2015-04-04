import json, boto, doWork, base64, time
import logging,sys
from boto.sqs.message import RawMessage
import aws_commons
import boto.sdb

userFileName = []

class Server():
    timeCounter = 5
    

    def __init__(self, **kwargs):
        self.clientQueueName = ''
        self.clients = set()
        self.finalDict = {}
        self.clientFileDict = {}

    def sendMessageToClient(self,clientName, fileName):
        queueName = clientName
 #       userFileName = ['file1','file2','file3']
        data = {}
        print 'Userfilename len %d' % len(userFileName)
        print 'Client queueName %s' % clientName
        data ={
 #           'fileName': userFileName
            'fileName': fileName

            }
        time.sleep(5)
        aws_commons.connectAndWriteToSQS(queueName, data)

    def storeMessageInSimpleDB(self, clientName, fileDict):
        # Item Name is file Hashvalue
        # Key is Clientname, Value is filename with abs path
        simpleDB = boto.sdb.connect_to_region('us-west-1')
        domain = simpleDB.create_domain('minbackup-domain')
        item_attrs = {}        
        for key,value in fileDict.items():
            item_attrs[clientName] = key
            domain.put_attributes(value,item_attrs,False)
            domain_meta = simpleDB.domain_metadata(domain)
        #retrievedItem = domain.get_item(value)
        domain_meta = simpleDB.domain_metadata(domain)
        print('1....Num of domain items: %d' % domain_meta.item_count)

    def dedup(self):
        unique = set()
        duplicates = []
        simpleDB = boto.sdb.connect_to_region('us-west-1')
        domain = simpleDB.lookup('minbackup-domain')
        if domain is None:
            return
        else:
            print 'Num of items in finalDict: %d' % len(self.finalDict)
            
            for hash in domain:
                print '\n'
                #print retrievedItem
                #print len(retrievedItem)
                retrievedItem = domain.get_item(hash.name)
                if len(retrievedItem) == 1:
                    print 'Just 1 file...need to ask client for file %s' % retrievedItem.values()[0]
                    self.sendMessageToClient(retrievedItem.keys()[0], retrievedItem.values()[0])
        
    def poll(self, wait=20, vtimeout=5):
        sqs = boto.connect_sqs()
        sqs = boto.sqs.connect_to_region('us-west-1')
        q = sqs.get_queue('server_queue')
        clientName = ''
        fileDict = {}
        q.set_message_class(RawMessage)
        while True:
            Server.timeCounter += 5
            print'Server waiting to poll for %d seconds' % Server.timeCounter
            time.sleep(Server.timeCounter)
            m = q.get_messages()
 #           print('Num of msgs in client queue: %s' % len(m))                
            if m:
                for result in m:
                    msg = json.loads(result.get_body())
 #                   self.finalDict.append(msg)
                    #print('Message %s' % msg)
                    userFileName.append(msg.get('filepath'))
                    #userFileName.append(msg.get('fileName'))
                    clientName = msg.get('clientQueueName')
                    fileDict = msg.get('fileDict')
                    #self.finalDict = fileDict
                    self.storeMessageInSimpleDB(clientName,fileDict)
                    #This below works with client-filedict map to store in sdb
                    #self.finalDict.setdefault(clientName,[]).append(fileDict)
                    self.clients.add(msg.get('clientQueueName'))
                    finalData ={
                        'client': msg.get('clientQueueName'),
                        'file': msg.get('filepath')
                        }
                    q.delete_message(result)

            else:
                print('Calculating files reqd....')
 #               self.dedup()
                
                time.sleep(5)
                if len(m) == 0:
                    #print('Writing to Client Q since nothing to read....')
                    self.dedup()
                    #iter = self.clients.__iter__()
                    #for s in iter:
                        #print(s)
                        #self.sendMessageToClient(s)
                    
            self.poll()
                                                  
server = Server()

#server.readMessage()
print('Polling Server q for msgs....')
#time.sleep(10)
server.poll()

#time.sleep(5)
#server.sendMessageToClient()
print('Done writint to Client Q')
