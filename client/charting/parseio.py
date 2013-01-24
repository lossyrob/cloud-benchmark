# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 12:39:27 2013

@author: rob
"""

import re
import os

d_fio = '/home/rob/proj/gt/demo/py/results/fio/'
d_gt = '/home/rob/proj/gt/demo/py/results/io_benchmark'


res = r'(?ms)usace-(?P<type>standard|provisioned|instance)-(?P<config>single|raid|storage): \(groupid.*?'
res += r'pid=(?P<pid>\d+).*?'
res += r'read : .*? bw=(?P<bw>[\d.]+)KB/s, iops=(?P<iops>[\d]+)[ ]*, runt=[ ]*(?P<runtime>\d+)msec'

class Result:
    def __init__(self, m):
        self.type = m.group('type')
        self.config = m.group('config')
        if self.config == 'storage':
            self.config = 'single'
        self.bw = m.group('bw')
        self.iops = m.group('iops')
        self.runtime = m.group('runtime')
        
class ResultSet:
    def __init__(self):
        self.results = {}
        for t in ['instance','standard','provisioned']:
            self.results[t] = {}
            for c in ['single','raid']:
                self.results[t][c] = []
                
    def add(self,result):
        self.results[result.type][result.config].append(result)
        
class GTResult:
    def __init__(self,txt):
        regx = r'\[CSV\] ([\d]+),([\d]+),([\d]+),([\d]+),([\d]+)'
        m = re.search(regx,txt)
        self.local = m.group(1)
        self.results = {}
        self.results['single'] = {}
        self.results['single']['standard'] = m.group(2)
        self.results['single']['provisioned'] = m.group(3)
        self.results['raid'] = {}
        self.results['raid']['standard'] = m.group(4)
        self.results['raid']['provisioned'] = m.group(5)
        
        
def dogt():
    results = []
    for f in map(lambda x: os.path.join(d_gt,x), os.listdir(d_gt)):
        txt = open(f).read()
        if not '[CSV]' in txt:
            continue
        print "Processing " + f
        results.append(GTResult(txt))
        
    gcsv = '"Type","Configuration","Time (ms)"\n'
    for r in results:
        gcsv += '"single","local","%s"\n' % (r.local)
        for t in ['single','raid']:
            for c in ['standard','provisioned']:
                gcsv += '"%s","%s","%s"\n' % (t,c,r.results[t][c])
    open(os.path.join(d_gt,"benchmark_results.csv"),'w').write(gcsv)
    
## Singles
def dosingle():
    singles = map(lambda x: os.path.join(d_fio,'single',x), os.listdir(os.path.join(d_fio,'single')))
    single_results = []
    for f in singles:
        txt = open(f).read()
        for m in re.finditer(res,txt):
            print m.group(0) + '\n%s  %s' % (m.group('type'), m.group('config'))
            single_results.append(Result(m))
    
    ## Write Results
    print "Total results: %d" % (len(single_results))
    print "Types: %s  Configs: %s" % (set(map(lambda r: r.type,single_results)),set(map(lambda r: r.config,single_results)))
    print "Singles: %s  RAIDs: %s" % (len(filter(lambda r: r.config == 'single',single_results)),len(filter(lambda r: r.config == 'raid',single_results)))
    
    scsv = '"Type","Configuration","IOPS","RunTime","BW"\n'
    for t in ['instance','standard','provisioned']:
        rs = filter(lambda r: r.type == t, single_results)
        print "Types of %s: %d" % (t,len(rs))
        for c in ['single','raid']:
                crs = filter(lambda r: r.config == c, rs)
                print "  Types of %s: %d" % (c,len(crs))
                for r in crs:          
                    scsv += '"%s","%s","%s","%s","%s"\n' % (r.type,
                                                            r.config,
                                                            r.bw,
                                                            r.iops,
                                                            r.runtime)
                                                            
    open(os.path.join(d_fio,'single_results.csv'),'w').write(scsv)

def dothreaded():                                                            
    ## Threaded 
    threadeds = map(lambda x: os.path.join(d_fio,'threaded',x), os.listdir(os.path.join(d_fio,'threaded')))
    threaded_results = []
    for f in threadeds:
        print "Processing " + f
        resultset = ResultSet()
        txt = open(f).read()
        for m in re.finditer(res,txt):
            resultset.add(Result(m))
            threaded_results.append(resultset)
            
    ## Write Results
            
    tcsv = '"Type","Configuration","IOPS","RunTime","BW","Thread"\n'
    for t in ['instance','standard','provisioned']:
        for c in ['single','raid']:
            for rs in threaded_results:
                for t in ['instance','standard','provisioned']:
                    for c in ['single','raid']:
                        count = 1
                                
                        for r in rs.results[t][c]:
                            tcsv += '"%s","%s","%s","%s","%s","%d"\n' % (r.type,
                                                                         r.config,
                                                                         r.bw,
                                                                         r.iops,
                                                                         r.runtime,
                                                                         count)
                            count += 1
                                                                                 
    open(os.path.join(d_fio,'threaded_results.csv'),'w').write(tcsv)
    print "Done."
    
dogt()
                                                                                         