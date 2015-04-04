import glob
import os
file_list = []
os.chdir("/Users/swetha/couch")
for files in glob.glob("*.*"):
    #print files
    file_list.append(files)

print len(file_list)    
for f in file_list:
    print f
