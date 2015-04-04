import boto,uuid,time, json
from uuid import getnode as get_mac
from boto.sqs.message import RawMessage

def __init__(self, **kwargs):
    pass

def connectAndWriteToSQS(queue, data):
    sqs = boto.connect_sqs()
    sqs = boto.sqs.connect_to_region('us-west-1')   
    q = sqs.create_queue(queue)
    m = RawMessage()
    m.set_body(json.dumps(data))
    q.write(m)

