# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 11:04:56 2013

@author: rob
"""

import csv
import operator

f_local = '/home/rob/proj/gt/demo/py/results/localrun/locally-run-results.csv'
f_client = '/home/rob/proj/gt/demo/py/results/vs-from-local/vs-results.csv'

class Header():
    def __init__(self,header_row):
        self.header_row = header_row
        
    def i(self,key):
        return self.header_row.index(key)

class Server():
    def __init__(self,servertype,storagetype):
        self.servertype = servertype
        self.storagetype = storagetype
        
    def __eq__(self,other):
        return self.servertype == other.servertype and self.storagetype == other.storagetype
        
    def __hash__(self):
        return hash(self.servertype) + hash(self.storagetype)
        
    def __str__(self):
        return "%s - %s" % (self.servertype,self.storagetype)

class Result():
    def __init__(self, header,row):
        self.req_per_conn = row[header.i("Req/Connections")]
        self.conn = row[header.i("Connections")]
        self.completed = row[header.i("Completed")]
        self.failed = row[header.i("Failed")]
        self.total = float(row[header.i("Total Time (s)")])
        self.transferred = row[header.i("Total transferred (bytes)")]
        self.req_sec = float(row[header.i("req/sec")])
        self.ms_per_req = float(row[header.i("msec/req")])
        self.ms_per_req_conc = row[header.i("msec/req concurrent")]
        self.kb_sec = row[header.i("KB/sec")]
        self.total_mean = float(row[header.i("Total mean (ms)")])
        self.total_std = float(row[header.i("Total std (ms)")])

class Benchmark():
    def __init__(self,name,size,rtype,req_source='local'):
        self.name = name
        self.size = size
        self.rtype = rtype
        self.req_source = req_source            
        
    def __eq__(self,other):
        return self.name == other.name and self.size == other.size and self.rtype == other.rtype and self.req_source == other.req_source

    def __hash__(self):
        return hash(self.name + self.size + self.rtype + self.req_source)
    
    def __str__(self):
        return "%s,%s,%s,%s" % (self.name,self.size,self.rtype,self.req_source)

results = {}

with open(f_local, 'rb') as f:
    reader = csv.reader(f)
    header = Header(reader.next())
    
        
    for row in reader:
        servertype = row[header.i('Server Type')]
        storagetype = row[header.i('Storage Type')]
        name = row[header.i('Test Name')]
        if '-con' in row[header.i('URL')]:
            name += ' - C'
        size = row[header.i('Custom')]
        rtype = row[header.i('Response Type')]
        
        b = Benchmark(name,size,rtype)
        s = Server(servertype,storagetype)
        
        if not b in results:
            results[b] = {}
        if not s in results[b]:
            results[b][s] = []
        
        results[b][s].append(Result(header,row))
        
with open(f_client, 'rb') as f:
    reader = csv.reader(f)
    header = Header(reader.next())
    
        
    for row in reader:
        servertype = row[header.i('Server Type')]
        storagetype = row[header.i('Storage Type')]
        name = row[header.i('Test Name')]
        if '-con' in row[header.i('URL')]:
            name += ' - C'
        size = row[header.i('Custom')]
        rtype = row[header.i('Response Type')]
        
        b = Benchmark(name,size,rtype,'client')
        s = Server(servertype,storagetype)
        
        if not b in results:
            results[b] = {}
        if not s in results[b]:
            results[b][s] = []
        
        results[b][s].append(Result(header,row))
        
servers = [s for b in results for s in results[b]]
print "Number of server types: %d" % len(set(servers))
ss = list(set(servers))
ss.sort(key=operator.attrgetter('servertype'))
for s in ss:
    def mp(b):
        if s in results[b]:
            return len(results[b][s])
        else:
            return 0
    lens = map(mp, results)
    print "%s : %s" % (s, lens)

def get_rate(server,benchmark):
    print '%s  %s' % (server,benchmark)
    s = sum(map(lambda r: r.req_sec, results[benchmark][server]))
    #s = sum(map(lambda r: r.total, results[benchmark][server]))
    #s = sum(map(lambda r: r.total_mean, results[benchmark][server]))
    c = len(results[benchmark][server])
    #stds = sum(map(lambda r: r.total_std, results[benchmark][server]))

    
    return s / float(c)
    
def get_mean(server,benchmark):
    #s = sum(map(lambda r: r.req_sec, results[benchmark][server]))
    #s = sum(map(lambda r: r.total, results[benchmark][server]))
    s = sum(map(lambda r: r.total_mean, results[benchmark][server]))
    #s = sum(map(lambda r: r.ms_per_req, results[benchmark][server]))
    c = len(results[benchmark][server])
    stds = sum(map(lambda r: r.total_std, results[benchmark][server]))

    print '%s  %s  %f %f' % (server,benchmark, s / float(c), stds / float(c))
    
    return (s / float(c), stds / float(c))

import numpy as np
import matplotlib.pyplot as plt

def plot(name,servers,benchmarks):
    
    N = len(benchmarks)
    ind = np.arange(N)  # the x locations for the groups
    width = 0.15       # the width of the bars
    fig = plt.figure(name)
    def rectsFor(s):
        return map(lambda b: get_mean(s,b[1])[0],benchmarks)

    def rateRectsFor(s):
        return map(lambda b: get_rate(s,b[1]),benchmarks)

    def barsFor(s):
       return map(lambda b: get_mean(s,b[1])[1],benchmarks)

    def plotTicks(p):
        p.xticks(ind+.29,map(lambda x: x[0],benchmarks))
    
    ax = fig.add_subplot(1,2,1)
    #plt.subplots_adjust(left=0.115, right=0.88)
    
    ax.set_title("Time per Request (ms)")
    
    for (i, (label,c,s)) in enumerate(servers):
        rects = rectsFor(s)
        bars = barsFor(s)
        plt.bar(ind+(i*width), rects, width, color=c, label=label, align='center',
                yerr=bars,
                error_kw=dict(elinewidth=4, ecolor='black'))
    
    plotTicks(plt)
    ax.legend(loc=1)
    
    ax = fig.add_subplot(1,2,2)
    ax.set_title("Requests Per Second")

    for (i, (label,c,s)) in enumerate(servers):
        rects = rateRectsFor(s)
        plt.bar(ind+(i*width), rects, width, color=c, label=label, align='center',)
    
    plotTicks(plt)
    ax.legend(loc=2)

local_benchmarks = [('Concurrent Hillshade', Benchmark('Hillshade - C','256x256','PNG')),
                   ('Weighted Overlay', Benchmark('Weighted Overlay','256x256','PNG')),]
                    
client_benchmarks = [Benchmark('Hillshade - C','256x256','PNG','client'),
                     Benchmark('Weighted Overlay','256x256','PNG','client')]
                    
lvc_benchmarks = [ ('Concurrent - Local', Benchmark('Hillshade - C','256x256','PNG')),
                   ('Weighted Overlay - Local', Benchmark('Weighted Overlay','256x256','PNG')),
                   ('Concurrent - Client', Benchmark('Hillshade - C','256x256','Text','client')),
                   ('Weighted Overlay - Client', Benchmark('Weighted Overlay','256x256','Text','client')),]
                   
lb_benchmarks = [ ('', Benchmark('Hillshade','256x256','PNG')) ]
                   
amazon_servers = [
                  ('m1.small',  '#FFCC00',   Server('m1.small','cache')),
                  ('m1.medium', '#FFAA00',   Server('m1.medium','cache')),
                  ('m1.large',  '#FF8800',   Server('m1.large','cache')),
                  ('m1.xlarge', '#FF5500',   Server('m1.xlarge','cache')),
                  ('m3.xlarge', '#FF0000',   Server('m3.xlarge','cache')),
                 ]
       


          
lb_servers = [
                  ('m1.medium (1)', '#FFBB00',   Server('m1.medium','cache')),
                  ('m1.medium (2)', '#FF5500',   Server('lb-m1.medium (2)','cache')),
                  ('m1.medium (4)', '#FF5500',   Server('lb-m1.medium (4)','cache')),
                  ('m1.large  (1)',  '#55BB77',   Server('m1.large','cache')),
                  ('m1.large  (2)', '#55BB33',   Server('lb-m1.large (2)','cache')),
                  ('m1.large  (4)', '#55BB00',   Server('lb-m1.large (4)','cache')),
                  ('m1.xlarge', '#FF0000',   Server('m1.xlarge','cache')),
                 ]

#plot('Small',
#     [('Amazon m1.medium',  'r',   Server('m1.medium','cache')),
#      ('Rackspace 4G',      'b',   Server('rackspace.4G','cache')),
#      ('HP Medium',         'g',   Server('hp.medium','cache'))],
#        local_benchmarks)

#plot('Small',
#     [('Amazon m1.xlarge',  '#FF5500',       Server('m1.xlarge','cache')),
#      ('Amazon m3.xlarge',  'r',       Server('m3.xlarge','cache')), 
#      ('HP Extra Large',    'g',       Server('hp.xlarge','cache'))],
#        local_benchmarks)

#plot('Amazon Servers',amazon_servers,local_benchmarks)
plot('Load Balancers',lb_servers,lb_benchmarks)

#plot('Client vs Local',
#     [
#      ('m1.large',   'r',   Server('m1.large','cache')),
#      ('m1.xlarge',   'm',   Server('m1.xlarge','cache')),
#      ], lvc_benchmarks)
      
plt.show()
