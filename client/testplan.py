from scenarios import *
from cloud.instances import *

DEBUG = None #'localhost:8000'

url_to_type = {}

def get_server(server_type):
    if DEBUG:
        return DEBUG
    if not server_type in url_to_type:
        running = filter(lambda ins: ins.instance_type == server_type, EC2Instances().running())
        url_to_type[server_type] = running[0].public_dns_name + ':8000'
    return url_to_type[server_type]

storages = ['cache','local','block']
servers = [
#           't1.micro',
           'm1.small',
#           'm1.medium',
           'm1.large',
#           'm1.xlarge',
#           'm3.xlarge'
           ]

def test_hp_vs_amazon():
    test_plan = {}

    # svs = { 
    #         'Rackspace 4G'     : '198.101.247.103:8000',
    #         'HP Medium'        : '15.185.97.80:8000',
    #         'Amazon m1.medium' : 'ec2-174-129-160-79.compute-1.amazonaws.com:8000',
    #         'Amazon m1.xlarge' : 'ec2-107-22-142-24.compute-1.amazonaws.com:8000',
    #         'Amazon m2.xlarge' : 'ec2-184-73-26-251.compute-1.amazonaws.com:8000',
    #         'HP Extra Large'   : '15.185.102.136:8000',
    #       }

    svs = dict(map(lambda x: (x,get_server(x)), servers))
    #svs = { 'localhost' : 'localhost:8000' }

    for s in svs:
        test_plan[svs[s]] = []
        for storage in ['cache','local']:
            for response in [True,False]:
                test_plan[svs[s]].append(OverlayScenario(s,'small',response,storage,500,20))
            test_plan[svs[s]].append(OverlayScenario(s,'med',False,storage,500,20))
        for storage in ['cache','local']:
            for concurrent in [True,False]:
                test_plan[svs[s]].append(HillshadeScenario(s,'small',True,5,storage,concurrent,500,20))

    return test_plan

def test_lb():
    test_plan = {}
    
    svs = { 'm1.medium' : get_server('m1.medium'),
            'lb-m1.medium (2)' : DEBUG or 'lb-medium-2-1419205817.us-east-1.elb.amazonaws.com',
            'lb-m1.medium (4)' : DEBUG or 'lb-medium-4-1950818059.us-east-1.elb.amazonaws.com',
            'lb-m1.large (2)' : DEBUG or 'lb-large-2-1750417607.us-east-1.elb.amazonaws.com',
            'lb-m1.large (4)' : DEBUG or 'lb-large-4-262195612.us-east-1.elb.amazonaws.com',
          }

    for s in svs:
        test_plan[svs[s]] = []
        for storage in storages:
            for storage in storages:
                test_plan[svs[s]].append(HillshadeScenario(s,'small',True,2,storage,False,500,10))

    return test_plan

def test_hs():
    test_plan = {}
    
    r = 500
    c = 10

    for s in servers[1:]:
        test_plan[get_server(s)] = []

    for s in servers[1:]:
        for storage in storages:
            for concurrent in [True,False]:
                test_plan[get_server(s)].append(HillshadeScenario(s,'small',True,2,storage,concurrent,r,c))

    for s in servers[2:]:
        for storage in storages:
            for concurrent in [True,False]:
                test_plan[get_server(s)].append(HillshadeScenario(s,'small',True,5,storage,concurrent,r,c))

    for s in servers[1:]:
        for storage in storages:
            for concurrent in [True,False]:
                test_plan[get_server(s)].append(HillshadeScenario(s,'small',True,10,storage,concurrent,50,5))

    return test_plan

def test_wo():
    test_plan = {}

    #### WO ####

    s = []
    t = 'm1.small'

    ## Response True
    for storage in ['cache','block','local']:
        s.append(OverlayScenario(t,'small',True,storage,200,10))
    for storage in ['cache','block','local']:
        s.append(OverlayScenario(t,'med',False,storage,50,5))
    for storage in ['cache','block','local']:
        s.append(OverlayScenario(t,'big',False,storage,10,1))

    test_plan[get_server(t)] = s
    
    s = []
    t = 'm1.medium'
    for response in [True,False]:
        for storage in ['cache','block','local']:
            s.append(OverlayScenario(t,'small',response,storage,200,10))
    for storage in ['cache','block','local']:
        s.append(OverlayScenario(t,'med',False,storage,100,10))
    for storage in ['cache','block','local']:
        s.append(OverlayScenario(t,'big',False,storage,10,10))

    test_plan[get_server(t)] = s

    s = []
    t = 'm1.large'

    for response in [True,False]:
        for storage in ['cache','block','local']:
            s.append(OverlayScenario(t,'small',response,storage,500,100))
    for response in [True,False]:
        for storage in ['cache','block','local']:
            s.append(OverlayScenario(t,'med',response,storage,500,100))
    for storage in ['cache','block','local']:
        s.append(OverlayScenario(t,'big',False,storage,500,100))
    
    test_plan[get_server(t)] = s
    s = []
    t = 'm1.xlarge'

    for response in [True,False]:
        for storage in ['cache','block','local']:
            s.append(OverlayScenario(t,'small',response,storage,500,100))
    for response in [True,False]:
        for storage in ['cache','block','local']:
            s.append(OverlayScenario(t,'med',response,storage,500,100))
    for storage in ['cache','block','local']:
        s.append(OverlayScenario(t,'big',False,storage,500,100))

    test_plan[get_server(t)] = s

    return test_plan
