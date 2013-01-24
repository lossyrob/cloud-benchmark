# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 17:33:42 2013

@author: rob
"""

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

volumes =  {
     'Amazon Standard' : (0.1,   lambda x: x * 0.1), # per Gigabyte provisioned per month, per 1 million IO requests
     'Amazon - 100 pIOPS'    : (0.125, lambda x: 10),  # per Gigabyte provisioned per month, per provisioned IOPS-month
     'Amazon - 500 pIOPS'    : (0.125, lambda x: 50),  # per Gigabyte provisioned per month, per provisioned IOPS-month
     'Amazon - 1000 pIOPS'    : (0.125, lambda x: 100),  # per Gigabyte provisioned per month, per provisioned IOPS-month
     'Amazon - 2000 pIOPS'    : (0.125, lambda x: 200),  # per Gigabyte provisioned per month, per provisioned IOPS-month
     'HP Standard' : (0.1,        lambda x: x * 0.1),  # per Gigabyte provisioned per month, per 1 million IO requests
     'Rackspace Standard': (0.15, lambda x: 0),
     'Rackspace SSD'     : (0.70, lambda x: 0),
}

v = [
     (0.1, 0.1,0,'y'), # per Gigabyte provisioned per month, per 1 million IO requests
     (0.125,0, 10,'r'),  # per Gigabyte provisioned per month, per provisioned IOPS-month
     (0.125,0,50,'r'),  # per Gigabyte provisioned per month, per provisioned IOPS-month
     (0.125,0,100,'r'),  # per Gigabyte provisioned per month, per provisioned IOPS-month
     (0.125,0, 200,'r'),  # per Gigabyte provisioned per month, per provisioned IOPS-month
     #(0.1,0.1,0,'y'),  # per Gigabyte provisioned per month, per 1 million IO requests
     (0.15, 0, 0,'b'),
#     (0.70, 0, 0,'b'),
]

snapshots = {
    'Amazon'       : 0.095,
    'HP'           : 0.1,
    'HP - Backups' : 0.12,
    'Rackspace'    : 0.1
}
 
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

# Get sane number of millions of IO requests per month.
totalsec = 2678400
# Just assume various IOP levels
usages = map(lambda x: x * totalsec / 1000000, [1,5,10,25,50,100,150,200,500,1000,2000])

#def plotone(perGB,perUsage,color):
#    xs = []
#    ys = []
#    zs = []
#    for usage in usages:
#        for gb in [5,10,50,100,250,500,750,1000]:
#            xs.append(gb)
#            ys.append(usage)
#            zs.append(gb*perGB + perUsage(usage))
#    # You can provide either a single color or an array. To demonstrate this,
#    # the first bar of each set will be colored cyan.
#    ax.plot_wireframe(xs, ys, zs, rstride=5,cstride=5,color=color, alpha=0.8)
#
#ax.set_xlabel('GB Provisioned')
#ax.set_ylabel('Data Usage')
#ax.set_zlabel('Price')
#
#for (perGB,perUsage,color) in v:
#    plotone(perGB,perUsage,color)
#
#plt.show()

#from mpl_toolkits.mplot3d import axes3d
#import matplotlib.pyplot as plt
#import numpy as np
#
#plt.ion()
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#

# Twice as wide as it is tall.
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.set_xlabel('GB Provisioned')
ax.set_ylabel('Data Usage')
ax.set_zlabel('Price')
    
def plotone2(perGB,perUsage,monthConst,color):
    X, Y = np.meshgrid([5,10,50,100,250,500,],usages)
    print X
    Z = X * perGB + monthConst + Y * perUsage
    ax.plot_surface(X, Y, Z, alpha=0.9,rstride=10, cstride=10,color=color,linewidth=0,antialiased=False)



#
#for angle in range(0, 360):
#    ax.view_init(30, angle)
#    plt.draw()
    
from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.pyplot as plt


# imports specific to the plots in this example
import numpy as np
from matplotlib import cm
from mpl_toolkits.mplot3d.axes3d import get_test_data



for (perGB,perUsage,monthConst,color) in v:
    plotone2(perGB,perUsage,monthConst,color)
    
#for (perGB,perUsage,monthConst,color) in v[-1:]:
#    X, Y = np.meshgrid([5,10,50,100,250,500,750,1000],usages)
#    Z = X * perGB + monthConst + Y * perUsage
#    ax.plot_wireframe(X, Y, Z, alpha=0.9,rstride=10, cstride=10,color=color,linewidth=0,antialiased=False)
#---- Second subplot


plt.show()