# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 11:35:18 2013

@author: rob
"""

import re
import os

d = '/home/rob/proj/gt/demo/py/results/benchmark/'

re_name = r'([^-]+)-([^-]+)-benchmark.([\d]+)'
re_time = r'benchmark=([^,]+), size=\d+} ([\d.]+) ns; σ=([\d.]+) ns'

class Result:
    def __init__(self,fname):
        self.path = os.path.join(d,fname)
        print fname
        m = re.match(re_name,fname)
        self.company = m.group(1)
        self.type = m.group(2)
        self.run = int(m.group(3))

files = os.listdir(d)
results = map(lambda x: Result(x), filter(lambda x: re.match(r'.*-benchmark.\d',x),os.listdir(d)))

csv = '"Company","Type","Run","Benchmark","Time (ns)","Std (ns)"\n'

for result in results:
    txt = open(result.path).read()
    for m in re.finditer(re_time,txt):
        csv += '"%s","%s","%d","%s","%s","%s"\n' % (result.company,
                                             result.type,
                                             result.run,
                                             m.group(1),
                                             m.group(2),
                                             m.group(3))

open(os.path.join(d,'benchmark-results.csv'),'w').write(csv)


                                            
        