    #get MAC Address
##    def sendMessageToServer(self):
##        queueName = 'server_queue'
##        print('In sendmsgtoserver client queue name is %s' % self.clientQueueName)
## #       mac = get_mac()
##        isDir = False
##        fileName = ''
##        data = {}
##        while True:
##            file_list = []
##            fileDict = {}
##            try:
##                if not self.dirEntered:
##                    self.reply = input('Enter directory:')
##                    print('This is the input directory for backup: %s' % self.reply)
##                    self.directory = self.reply
##                    isDir = os.path.isdir(self.directory)
##                    if not isDir:
##                        print 'Invalid Dir. Enter correct one'
##                        continue
##                    if isDir:
##                        self.dirEntered = True
##                        os.chdir(self.directory)
##                        #for files in glob.glob("*.*"):
##                        for path, dirs, files in walk( self.directory ):
##                            file_list.append(files)                        
##                        #from fileInfo import FileInfo
##                        #for fileName in file_list:
##                        for filename in files:
##                            with open(fileName) as openfile:
##                                fileHash = md5(openfile.read()).hexdigest()
##                            filepath = joinpath( path, filename )
##                            print 'Filepath %s' % filepath
##                            fileDict.setdefault(filepath,[]).append(fileHash)
##                            #fileDict.setdefault(fileName,[]).append(fileHash)
##                        data ={
##                            'clientQueueName': self.clientQueueName,
##                            'fileDict': fileDict
##                            }
##                        aws_commons.connectAndWriteToSQS(queueName, data)
##
##            # This else should never execute
##                else:
##                    print('Directory already enter...Using existing.. %s' % self.directory)
##                    os.chdir(self.directory)
##                    for files in glob.glob("*.*"):
##                        file_list.append(files)
##                        data ={
##                            'fileName': file_list,
##                            'clientQueueName':self.clientQueueName
##                            }
##                        aws_commons.connectAndWriteToSQS(queueName, data)
##
####                    for fName in file_list:
####                        fileName = fName
####                        print 'Writing file to Server queue %s' % fName
####                        data ={
####                            'fileName': fileName,
####                            'clientQueueName': self.clientQueueName
####                            }
####                        aws_commons.connectAndWriteToSQS(queueName, data)
##
##            except IOError:
##                print 'Invalid Dir..........exception Enter correct one'
##                continue
####            except:
####                print 'Invalid Value. Enter correct one'
####                continue
##            break
##        self.poll()
