import subprocess,re
from collections import OrderedDict

class ApacheBench:
    """A session of 'ab', the Apache HTTP server benchmarking tool.

Example output from ab:

This is ApacheBench, Version 2.0.40-dev <$Revision: 1.121.2.1 $> apache-2.0
Copyright (c) 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Copyright (c) 1998-2002 The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
nnCompleted 800 requests
Completed 900 requests


Server Software:        CherryPy/3.1beta
Server Hostname:        127.0.0.1
Server Port:            54583

Document Path:          /static/index.html
Document Length:        14 bytes

Concurrency Level:      10
Time taken for tests:   9.643867 seconds
Complete requests:      1000
Failed requests:        0
Write errors:           0
Total transferred:      189000 bytes
HTML transferred:       14000 bytes
Requests per second:    103.69 [#/sec] (mean)
Time per request:       96.439 [ms] (mean)
Time per request:       9.644 [ms] (mean, across all concurrent requests)
Transfer rate:          19.08 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   2.9      0      10
Processing:    20   94   7.3     90     130
Waiting:        0   43  28.1     40     100
Total:         20   95   7.3    100     130

Percentage of the requests served within a certain time (ms)
  50%    100
  66%    100
  75%    100
  80%    100
  90%    100
  95%    100
  98%    100
  99%    110
 100%    130 (longest request)
Finished 1000 requests
"""    
    fields = OrderedDict([
        ('Completed' , r'^Complete requests:\s*(\d+)'),
        ('Failed' , r'^Failed requests:\s*(\d+)'),
        ('Total Time (s)' , r'^Time taken for tests:\s*([0-9.]+)'),
        ('Total transferred (bytes)' , r'^Total transferred:\s*([0-9.]+)'),
        ('req/sec' , r'^Requests per second:\s*([0-9.]+)'),
        ('msec/req' , r'^Time per request:\s*([0-9.]+).*mean\)$'),
        ('msec/req concurrent' , r'^Time per request:\s*([0-9.]+).*concurrent requests\)$'),
        ('KB/sec' , r'^Transfer rate:\s*([0-9.]+)'),
        ('Connect mean (ms)' , r'^Connect:\s*[0-9.]+\s*([0-9.]+)'),
        ('Connect std (ms)' , r'^Connect:\s*[0-9.]+\s*[0-9.]+\s*([0-9.]+)'),
        ('Processing mean (ms)' , r'^Processing:\s*[0-9.]+\s*([0-9.]+)'),
        ('Processing std (ms)' , r'^Processing:\s*[0-9.]+\s*[0-9.]+\s*([0-9.]+)'),
        ('Waiting mean (ms)' , r'^Waiting:\s*[0-9.]+\s*([0-9.]+)'),
        ('Waiting std (ms)' , r'^Waiting:\s*[0-9.]+\s*[0-9.]+\s*([0-9.]+)'),
        ('Total mean (ms)' , r'^Total:\s*[0-9.]+\s*([0-9.]+)'),
        ('Total std (ms)' , r'^Total:\s*[0-9.]+\s*[0-9.]+\s*([0-9.]+)'),
        ])
    
    @staticmethod
    def run(req,concur,addr):
        # Parse output of ab, setting attributes on self
        try:
            cmd = ["ab",
             "-c",str(concur),
             "-n",str(req),
             "-v","2",
             addr]

            output = subprocess.check_output(["ab",
                                              "-c",str(concur),
                                              "-n",str(req),
                                              "-v","2",
                                              addr])
        except:
            print("Running Apache Bench failed. Make sure apache2-utils is installed")
            raise
        
        result = { 'requests' : req, 'concurrency' : concur, 'address' : addr }

        if 'WARNING: Response code not 2xx' in output:
           result['error'] = True
        else:
           result['error'] = False

        for name, pattern in ApacheBench.fields.items():
            val = re.search(pattern, output, re.MULTILINE)
            if val:
                val = val.group(1)
                result[name] = val
            else:
                result[name] = None

        return result
