class clientPoll():
    
    def poll(self, wait=20, vtimeout=5):
        sqs = boto.connect_sqs()
        sqs = boto.sqs.connect_to_region('us-west-1')
        print('Client Queue Polling will being in 2 mins for any new messages.... %s' % self.clientQueueName)
        q = sqs.get_queue(self.clientQueueName)
        q.set_message_class(RawMessage)
        while True:
            time.sleep(120)
            print('Waiting for server for 120 seconds....')
            m = q.get_messages(10)
            print('Num of msgs in my queue: %d' % len(m))
            #if there are messages in client q, read them and delete msgs
            if m:
                for result in m:
                    msg = json.loads(result.get_body())
                    fileName = msg.get('fileName')
                    fileHash = msg.get('fileHash')
                    print 'filename: %s' % fileName
                    print 'fileHash: %s' % fileHash
                    if msg.get('restore') is not None:
                        print msg.get('restore')
                    elif fileName is not None and fileHash is not None:
                        self.uploadFileToS3(fileName, fileHash)
                    q.delete_message(result)
                    print 'Done...Messages deleted from queue'
 # Following code just uncommented....for writing to server continuously
 #every 1.1 mins                   
            else:
                if len(m) == 0:
                    print('Writing to Server Q since nothing to read....')
                    self.sendMessageToServer()
            self.poll()

def main(argv):
    queueName = ''
    dirName = ''
    try:
        opts, args = getopt.getopt(argv,"hq:",["queueName="])
    except getopt.GetoptError:
        print 'client.py -q <queueName>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'client.py -q <queueName>'
            sys.exit()
        elif opt in ("-q", "--queueName"):
            queueName = arg
    print 'Client queue Name is "', queueName
    print 'Dir Name is "', dirName
    client = Client()
    client.createClientQueue(queueName, dirName)
 

if __name__ == "__main__":
    main(sys.argv[1:]) 
