import dircache
list = dircache.listdir('/Users/swetha/couch')
i = 0
check = len(list[0])
temp = []
count = len(list)
while count != 0:
  if len(list[i]) != check:
     temp.append(list[i-1])
     check = len(list[i])
  else:
    i = i + 1
    count = count - 1

print temp
