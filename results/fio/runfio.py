import subprocess
import re, os

if os.listdir('single'):
  i=max(map(lambda x: int(re.match(r'result(\d+)',x).group(1)),os.listdir("single"))) + 1
else:
  i = 0

while True:
  print ("Running %d" % i)
  subprocess.call("fio single-fiojob.conf > single/result%d" % i,shell=True)
  subprocess.call("fio fiojob.conf > threaded/result%d" % i,shell=True)
  i += 1
