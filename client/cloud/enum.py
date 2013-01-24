def enum(**enums):
    return type('Enum', (), enums)

InstanceState = enum(PENDING=0,
                     RUNNING=16,
                     SHUTTINGDOWN=32,
                     TERMINATED=48,
                     STOPPING=64,
                     STOPPED=80)


# ( Memory [GB], Instance Storage Capacity [GB], CPUs, Price )
server_info = { 'Rackspace' : {
 '512MB'      : (0.5,20,1,0.022),
 '1GB'        : (1,40,1,0.06),
 '2GB'        : (2,80,2,0.12),
 '4GB'        : (4,160,2,0.24),
 '8GB'        : (8,320,4,0.48),
 '15GB'       : (15,620,6,0.90),
 '30GB'       : (30,1200,8,1.20) },
  'Amazon' : {
 't1.micro'    : ( 0.6,      0,   1.5,    0.02),
 'm1.small'    : ( 1.7,    160,   1,    0.065),
 'm1.medium'   : ( 3.75,   410,   2,    0.13),
 'm1.large'    : ( 7.5,    850,   4,    0.26),
 'm1.xlarge'   : (15,     1690,   8,    0.52),
 'm3.xlarge'   : (15,        0,  13,    0.58),
 'm3.2xlarge'  : (30,        0,  26,    1.16),
 'm2.xlarge'   : (17.1,    420,   6.5,  0.45),
 'm2.2xlarge'  : (34.2,    850,  13,    0.9),
 'm2.4xlarge'  : (68.4,   1690,  26,    1.8),
 'c1.medium'   : ( 1.7,    350,   5,    0.165),
 'c1.xlarge'   : ( 7,     1690,  20,    1.140),
 'cc2.4xlarge' : (23,     1680,  33.5,  1.30),
 'cc2.8xlarge' : (60.5,   3370,  88,    2.40),
 'cg1.4xlarge' : (22,     1690,  33.5,  2.10),
 'hi1.4xlarge' : (60.5,   1024,  35,    3.10),
 'hs1.8xlarge' : (117,   49152,  35,    4.60) } }
