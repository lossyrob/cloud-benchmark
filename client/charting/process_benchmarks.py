# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 11:18:56 2013

@author: rob
"""
import csv
import operator

f = '/home/rob/proj/gt/demo/py/results/benchmark/benchmark-results.csv'

tests = [
('IntArrayWhileLoop', 'IntArrayLoop'),
('DoubleArrayWhileLoop','DoubleArrayLoop'),
('RasterWhileLoop','RasterLoop'),
('RasterMap','RasterMap'),
('RasterMapIfSet','RasterMapIfSet'),
#'BitDataWhileLoop',
#'BitDataMap',
('ByteDataWhileLoop','ByteLoop'),
('ByteDataMap','ByteMap'),
('ShortDataWhileLoop','ShortLoop'),
('ShortDataMap','ShortMap')
]

mixed_servers = [
#('m1.small','r'),
#('4G','b'),
#('m1.medium','r'),
#('medium','g'),
#('m1.large','r'),
('m1.xlarge','#FF5500'),
('m3.xlarge','r'),
('xlarge','g'),
]

amazon_servers = [
('m1.small','#FFCC00'),
('m1.medium','#FFAA00'),
('m1.large','#FF8800'),
('m1.xlarge','#FF5500'),
('m3.xlarge','#FF0000'),
]
                 
tick_offset = .22

class Result:
    def __init__(self,company,typ,test,time,std):
        self.company = company
        self.typ = typ
        self.test = test
        self.time = float(time) / 1000000.0 # Convert to ms
        self.std = float(std) / 1000000.0
        
    def __str__(self):
        return "Result: %s  %s %s %f  %f" % (self.company,self.typ,self.test,self.time,self.std)


results = []
with open(f, 'rb') as f:
    reader = csv.reader(f)
    header = reader.next()
        
    for row in reader:
        company = row[0]
        typ = row[1]
        test = row[3]
        time = row[4]
        std = row[5]
        results.append(Result(company,typ,test,time,std))
        
# Order by test
results.sort(key=operator.attrgetter('typ'))

test_results = {}
server_results = {}
for r in results:
    if not r.test in test_results:
        test_results[r.test] = []
    test_results[r.test].append(r)
    
    if not r.typ in server_results:
        server_results[r.typ] = []
    server_results[r.typ].append(r)

print len(test_results)
for t in test_results:
    print t
    
print
print len(server_results)
for s in server_results:
    print s

#for s in server_results:
#    for r in server_results[s]:
#        print "%s" % r

def plotit(servers): 
    import numpy as np
    import matplotlib.pyplot as plt
    
    def get_mean(server,test):
        print "Getting for %s - %s" % (server,test)
        #s = sum(map(lambda r: r.req_sec, results[benchmark][server]))
        #s = sum(map(lambda r: r.total, results[benchmark][server]))
        s = sum(map(lambda r: r.time, filter(lambda r: r.test == test, server_results[server])))
        #s = sum(map(lambda r: r.ms_per_req, results[benchmark][server]))
        c = len(filter(lambda r: r.test == test, server_results[server]))
        std = sum(map(lambda r: r.std, filter(lambda r: r.test == test, server_results[server])))
        return (s / float(c), std / float(c))

    N = len(tests)
    ind = np.arange(N)          # the x locations for the groups
    width = 0.1                 # the width of the bars
    fig = plt.figure("Benchmark Results")
    def rectsFor(s):
        return map(lambda (t,_): get_mean(s,t)[0],tests)

    def barsFor(s):
       return map(lambda (t,_): get_mean(s,t)[1],tests)

    def plotTicks(p):
        p.xticks(ind+tick_offset,map(lambda (_,l):l,tests))

    ax = fig.add_subplot(111)
    ax.set_title("Benchmark Results (ms)")

    for (i, (s,c)) in enumerate(servers):
        print s
        rects = rectsFor(s)
        bars = barsFor(s)
        print len(rects)
        print len(bars)
        plt.bar(ind+(i*width), rects, width, color=c, 
                label=s, align='center',
                yerr=bars,
                error_kw=dict(elinewidth=4, ecolor='black'))

    plotTicks(plt)
    ax.legend(loc=1)

    plt.show()

plotit(amazon_servers)
