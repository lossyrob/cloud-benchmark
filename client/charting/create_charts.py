# -*- coding: utf-8 -*-
"""
For plotting server options from Amazon, HP, and Rackspace,
according to CPUs, Memory, Storage, and Price per hour.
"""

import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import pylab as P

# PRICES FROM 1/18/2013
# EC2 Prices from On-Demand instances in US East (N. Virginia) Region
# ( Image set 3)

def GiB_to_GB(gib):
    return gib / 1.074

s_s = {
'512MB'      :  (0.5,                 20,1,0.022,'b'),
't1.micro'    : (GiB_to_GB(0.6),      0,   1.5,    0.02,'r'),
 '1GB'        : (1,                   40,1,0.06,'b'),
'Extra Small' : (1,                   30,1,0.035,'g'),
'm1.small'    : (GiB_to_GB(1.7),     160,   1,    0.065,'r'),
'c1.medium'   : (GiB_to_GB(1.7),     350,   5,    0.165, 'r'),
 '2GB'        : (2,                   80,2,0.12,'b'),
'Small'       : (2,                   60,2,0.07,'g'),
 'm1.medium'  : (GiB_to_GB(3.75),    410,   2,    0.13, 'r'),   # Marked for benchmark
 '4GB'        : (4,                  160,   2,    0.24, 'b'),   # Marked for benchmark
 'Medium'     : (4,                  120,   4,    0.14,'g'),    # Marked for benchmark
 }

s_m = {
'c1.xlarge'   : (GiB_to_GB(7),      1690,  20,   0.66, 'r'),
'm1.large'    : (GiB_to_GB(7.5),     850,   4,    0.26, 'r'), 
'8GB'         : (8,                  320,   4,    0.48, 'b'),
'Large'       : (8,                  240,   8,    0.28, 'g'),
'15GB'        : (15,                 620,   6,    0.90,'b'),
'm1.xlarge'   : (GiB_to_GB(15),     1690,   8,    0.52,'r'),   # Marked for benchmark
'm3.xlarge'   : (GiB_to_GB(15),        0,  13,    0.58,'r'),   # Marked for benchmark
'Extra Large' : (16,                 480,  16,    0.56,'g'),   # Marked for benchmark
'm2.xlarge'   : (GiB_to_GB(17.1),    420,  6.5,   0.45,'r'),
}

s_l = {
'cc2.4xlarge' : (GiB_to_GB(23),     1680,  33.5,  1.30,  'm'),
'cg1.4xlarge' : (GiB_to_GB(22),     1690,  33.5,  2.10,  'y'),
'm3.2xlarge'  : (GiB_to_GB(30),        0,  26,    1.16,  'r'),
'm2.2xlarge'  : (GiB_to_GB(34.2),    850,  13,    0.9,   'r'),
'30GB'        : (30,                1200,   8,    1.20,  'b'),
'Double Extra Large' : (32,          960, 32,   1.12,  'g')
 }
 
s_xl = {
 'm2.4xlarge'  : (GiB_to_GB(68.4),   1690,  26,    1.8, 'r'),
 'cc2.8xlarge' : (GiB_to_GB(60.5),   3370,  88,    2.40, 'm'),
 'hi1.4xlarge' : (GiB_to_GB(60.5),   1024,  35,    3.10, 'r'),
 'hs1.8xlarge' : (GiB_to_GB(117),   49152,  35,    4.60, 'r')
}
 
def create_figure(name, d,mul,zerosize):
    fig = plt.figure(name)
    ax = fig.add_subplot(111, projection='3d')
    
    ax.set_xlabel('Memory (GB)')
    ax.set_ylabel('CPUs')
    ax.set_zlabel('Price (US$)')
    
    maxprice = max(map(lambda x: d[x][3],d))
    minmem = min(map(lambda x: d[x][0],d))
    maxmem = max(map(lambda x: d[x][0],d))
    
    #ax.set_xlim(0, 1)
    #ax.set_ylim(0, 1)
    ax.set_zlim(0, maxprice)
    ax.set_xlim(minmem - 0.5, maxmem + 0.5)

    for server in d:
        memory =   d[server][0]
        storage = d[server][1]
        cpu   =   d[server][2]
        price  =   d[server][3]
        marker = 'o'
        color = d[server][4]
        if storage == 0:
            marker = '*'
            storage = zerosize
        
                
        ax.scatter([memory],
                   [cpu],
                [price],
                s=[storage*mul],c=color,marker=marker)
        ax.bar([memory],
           [cpu],
           zs=[0],
           zdir='z',
           color='b',
           alpha=0.1,
           width=0.01)
        ax.bar([memory],
           [cpu],
           zs=[price],
           zdir='z',
           color=color,width=0.01)
        ax.scatter([memory],
                   [cpu],
                [0],
                s=[zerosize*mul*0.5],c=color,marker='s',alpha=0.1)

mul = { 's' : 1,
      'm' : 3/5.0,
      'l' : 2/5.0,
      'xl' : 2/5.0 }

s = (s_s,mul['s'],100)
m = (s_m,mul['m'],300)
l = (s_l,mul['l'],700)
xl = (s_xl,mul['xl'],700)

create_figure("Small",*s)
create_figure("Medium",*m)
create_figure("Large",*l)
create_figure("Extra Large",*xl)

plt.show()
