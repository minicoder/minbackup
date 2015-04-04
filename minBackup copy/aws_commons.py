import boto,uuid,time, json
from uuid import getnode as get_mac
from boto.sqs.message import RawMessage

def __init__(self, **kwargs):
    pass

##def connectToS3(self):
##        s3 = boto.connect_s3()
##        bucket = s3.create_bucket('message_pump.minbackup.com')
##        key = bucket.new_key('examples/first_file.csv')
##        key.set_contents_from_filename('/Users/swetha/ENV/minBackup/first_file.csv')

def connectAndWriteToSQS(queue, data):
    #print('In AWS Commons..writng to q: %s' % queue)
    #print('In AWS Commons..Data: %s' % data)
    sqs = boto.connect_sqs()
    sqs = boto.sqs.connect_to_region('us-west-1')   
    q = sqs.create_queue(queue)
    m = RawMessage()
 #   time.sleep(10)
    m.set_body(json.dumps(data))
    q.write(m)

def createQueue(queue):
    sqs = boto.connect_sqs()
    sqs = boto.sqs.connect_to_region('us-west-1')
    queueExists = sqs.lookup(queue)
##    if queueExists == None:
##        q = sqs.create_queue(queue)
##    else:
##        

    ##    def connectToSQS(self, data):
##        sqs = boto.connect_sqs()
##        sqs = boto.sqs.connect_to_region('us-west-1')
##        q = sqs.create_queue('msg_q_to_server')
##        m = RawMessage()
##        time.sleep(10)
##        m.set_body(json.dumps(data))
##        q.write(m)
    
        
##    def connectToSQS(self,message):
##        sqs = boto.connect_sqs()
##        sqs = boto.sqs.connect_to_region('us-west-1')
##        q = sqs.create_queue('my_message_queue')
##        data ={
##            'submitdate': time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
##            'key': str(uuid.uuid1()),
##            'message' : str(message)
##            }
##        data1 = simplejson.dumps(data)
##        s3 = boto.connect_s3()
##        bucket = s3.get_bucket('message_pump.minbackup.com')
##        key = bucket.new_key('2013-09-02/%s.json' % str(uuid.uuid4()))
##        key.set_contents_from_string(data1)
##        message = q.new_message(body=simplejson.dumps({'bucket':bucket.name,'key':key.name}))
##        q.write(message)
