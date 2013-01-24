# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 16:27:55 2013

@author: rob
"""
import math, os

io_gt = '/home/rob/proj/gt/demo/py/results/io_benchmark/'

def getiogtresult():
    txt = open(os.path.join(io_gt,'benchmark_results.csv')).read()
    lines = map(lambda line: map(lambda x: x.strip('"'),line.split(',')),txt.split('\n')[1:])
    results = {}
    for l in filter(lambda x: len(x) == 3,lines):
        config= l[0]
        t = l[1]
        time = int(l[2])
        if not t in results:
            results[t] = {}
        if not config in results[t]:
            results[t][config] = []
        results[t][config].append(time)
    return results

def doiogt():
    results = getiogtresult()
    totalmin = 1000000000
    totalmax = 0
    csv = '"Type","Count","Mean","Min","Max","Std"\n'
    for t in results:
        for config in results[t]:
            ts = "%s - %s" % (t,config)
            s = sum(results[t][config])
            c = len(results[t][config])
            mean = s/float(c)
            m = min(results[t][config])
            M = max(results[t][config])
            totalmin = min([m,totalmin])
            totalmax = max([M,totalmax])
            std = math.sqrt(sum(map(lambda x: (x - mean)*(x - mean),results[t][config])) / (c-1))
            csv += '"%s","%d","%f","%f","%f","%f"\n' %  (ts,c,mean,m,M,std)

    def get_hist(s):
        buckets = {}
        for m in range(3500,7000,100):
            buckets[m] = len(filter(lambda x: m <= x and x <= m+100,s))
        return buckets
        
    for t in results:
        for config in results[t]:
            csv += '\n\"nHistogram - %s - %s"\n' % (t,config)
            h = get_hist(results[t][config])
            for m in range(3500,7000,100):
                csv = "%d,
            
            
    open(os.path.join(io_gt,'processed_results.csv'),'w').write(csv)
    
    
doiogt()