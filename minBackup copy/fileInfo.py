#!/usr/bin/python

class FileInfo():
    counter = 0
    unique = set()
    duplicates = []

##    def __init__(self, name, fileHash):
##        self.name = name
##        self.fileHash =  fileHash
##        FileInfo.counter += 1

    def __init__(self, name):
        self.name = name
        FileInfo.counter += 1
        
    def displayFileCount(self):
        print 'Total Num of Files %d' % FileInfo.counter

    def displayFileInfo(self):
        print 'File Name: %s' % self.name
       # print 'Hashvalue of file: %s' % self.fileHash


    def getData(self):            
        self.displayFileCount()
        self.displayFileInfo()
        data ={
            'fileName': self.name
 #           'fileHash': self.fileHash
            }
        return data
