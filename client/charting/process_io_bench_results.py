# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 16:27:55 2013

@author: rob
"""
import os
import numpy as np
import pylab as P

io_gt = '/home/rob/proj/gt/demo/py/results/io_benchmark/'
io_fio = '/home/rob/proj/gt/demo/py/results/fio/'

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
    return np.array([results['local']['single'],
             results['standard']['single'],
             results['standard']['raid'],
             results['provisioned']['single'],
             results['provisioned']['raid']], np.int32).transpose()

def getfioresult(key = 'iops'):
    txt = open(os.path.join(io_fio,'single_results.csv')).read()
    lines = map(lambda line: map(lambda x: x.strip('"'),line.split(',')),txt.split('\n')[1:])
    results = {}
    for l in filter(lambda x: len(x) == 5,lines):
        config= l[1]
        t = l[0]
        x = {}
        x['iops'] = int(l[2])
        x['runtime'] = int(l[3])
        x['bw'] = int(l[4])
        if not t in results:
            results[t] = {}
        if not config in results[t]:
            results[t][config] = []
        results[t][config].append(x)
        
    def getfor(t,config):
        return map(lambda x: x[key],results[t][config])
    
    return np.array([getfor('instance','single'),
             getfor('standard','single'),
             getfor('standard','raid'),
             getfor('provisioned','single'),
             getfor('provisioned','raid')], np.int32).transpose()


#results = getiogtresult()
#totalmin = 1000000000
#totalmax = 0

#csv = '"Type","Count","Mean","Min","Max","Std"\n'
#for t in results:
#    for config in results[t]:
#        ts = "%s - %s" % (t,config)
#        s = sum(results[t][config])
#        c = len(results[t][config])
#        mean = s/float(c)
#        m = min(results[t][config])
#        M = max(results[t][config])
#        totalmin = min([m,totalmin])
#        totalmax = max([M,totalmax])
#        std = math.sqrt(sum(map(lambda x: (x - mean)*(x - mean),results[t][config])) / (c-1))
#        csv += '"%s","%d","%f","%f","%f","%f"\n' %  (ts,c,mean,m,M,std)

# provisioned - single
# provisioned - raid
# local - single
# standard - single
# standard - raid

gt = getiogtresult()
iops = getfioresult('iops') 
runtime = getfioresult('runtime') 


h, w = 3, 1

            
P.figure()

P.subplot(2,1,1)
P.title("FIO Runtime")

n, bins, patches = P.hist(runtime, 20, histtype='bar',
                            color=['green', 'red', 'm','cyan','blue'],
                            label=['Local Storage', 
                                   'Standard - Single Volume', 
                                   'Standard - 16 Volumes in RAID 0',
                                   'pIOPs - Single Volume',
                                   'pIOPs - 16 Volumes RAID 0'])

P.legend()

P.subplot(2,1,2)
P.title("FIO IOPS")
                                   
n, bins, patches = P.hist(iops, 20, histtype='bar',
                            color=['green', 'red', 'm','cyan','blue'],
                            label=['Local Storage', 
                                   'Standard - Single Volume', 
                                   'Standard - 16 Volumes in RAID 0',
                                   'pIOPs - Single Volume',
                                   'pIOPs - 16 Volumes RAID 0'])
                                   

P.legend()
#
# ... or we can stack the data
#

P.show()

def get_hist(s):
    buckets = {}
    for m in range(3500,7000,100):
        buckets[m] = len(filter(lambda x: m <= x and x <= m+100,s))
    return buckets
    
med_compare = ['hp.medium','m1.medium']
    
#for t in results:
#    for config in results[t]:
#        csv += '\n\"nHistogram - %s - %s"\n' % (t,config)
#        h = get_hist(results[t][config])
#        for m in range(3500,7000,100):
#            pass
            
            
