import uuid
import time
import json
import boto
from boto.sqs.message import RawMessage
from boto.sqs.connection import SQSConnection

testQueue="testQueue"

def addMessage(message):
        data={
                'submitdate': time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                'key': str(uuid.uuid1()),
                'message': str(message)
                }
        conn = SQSConnection()
        conn = boto.connect_sqs()
        m = RawMessage()
        m.set_body(json.dumps(data))
        status=q.write(m)

def readMessageFromQueue():
        sqs = boto.connect_sqs(AWSKey, AWSSecret)
        q = sqs.create_queue(testQueue)
        q.set_message_class(RawMessage)
 
    # Get all the messages in the queue
        results = q.get_messages()
        ret = "Got %s result(s) this time.\n\n" % len(results)
 
        for result in results:
                msg = json.loads(result.get_body())
                ret += "Message: %s\n" % msg['message']

        print 'Hello... '+ret
        ret += "\n... done."
        return ret
