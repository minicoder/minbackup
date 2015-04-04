import json, boto, uuid, time, base64, sys, getopt
from uuid import getnode as get_mac
from os import walk, remove, stat
from os.path import join as joinpath
from boto.sqs.message import RawMessage
import glob, os, aws_commons
from datetime import datetime
from md5 import md5

def loopThrough(path_to_dir):
    fileiter = (os.path.join(root, f)
                for root, _, files in os.walk(path_to_dir)
                for f in files)
    print fileiter


def main(argv):
    queueName = ''
    dirName = ''
    try:
        opts, args = getopt.getopt(argv,"hd:",["queueName="])
    except getopt.GetoptError:
        print 'client.py -q <queueName>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'client.py -q <queueName>'
            sys.exit()
        elif opt in ("-d", "--dirName"):
            dirName = arg
    print 'Dir Name is "', dirName
    loopThrough(dirName)
 

if __name__ == "__main__":
    main(sys.argv[1:]) 
