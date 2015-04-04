import json as simplejson, boto, uuid, time

def connectToSQS(message='Hello.....Through pgm'):
    
    sqs = boto.connect_sqs()
    sqs = boto.sqs.connect_to_region('us-west-1')
    q = sqs.create_queue('my_message_queue')
    data ={
        'submitdate': time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        'key': str(uuid.uuid1()),
        'message' : str(message)
        }
    data1 = simplejson.dumps(data)
    s3 = boto.connect_s3()
    bucket = s3.get_bucket('message_pump.minbackup.com')
    key = bucket.new_key('2013-09-02/%s.json' % str(uuid.uuid4()))
    key.set_contents_from_string(data1)
    message = q.new_message(body=simplejson.dumps({'bucket':bucket.name,'key':key.name}))
    q.write(message)
