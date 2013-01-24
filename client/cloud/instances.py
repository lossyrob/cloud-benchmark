import ConfigParser, os
from boto import ec2
from boto.ec2 import elb
from enum import *

def get_price(server):
    if server in server_info['Amazon']:
        return server_info['Amazon'][server][3]
    else:
        return server_info['Rackspace'][server][3]

def calculate_hourly():
    ec2_singles = list(set(ec2_servers.keys()) - set(ec2_load_balancers[4].keys()))
    ec2_fours = list(ec2_load_balancers[4].keys())

    total = 0.0
    total += sum(map(lambda s: get_price(s), ec2_singles))
    total += 4 * sum(map(lambda s: get_price(s), ec2_fours))
    return total

class EC2Instances():
    def __init__(self):
        self.con = self.get_connection()
        
    def instances(self):
        return [ins for r in self.con.get_all_instances() for ins in r.instances]

    def running(self):
        f = { 'instance-state-code' : InstanceState.RUNNING }
        return [ins for r in self.con.get_all_instances(filters = f) for ins in r.instances]

    def start(self,typ):
        return self.con.run_instances('ami-ddcd46b4',instance_type=typ,security_groups=['trellis'])

    def get_connection(self):
        
        config = ConfigParser.ConfigParser()

        config.readfp(open(os.path.expanduser('~/.boto')))

        return ec2.EC2Connection(config.get('Credentials','aws_access_key'),
                             config.get('Credentials','aws_secret_access_key'))


#class EC2LoadBalancers():
#    def __init__(self):
        
        
        
server_params = {
    't1.micro' : (100,5),
    '512MB'    : (100,5)
}

server_raster_sizes = {
    't1.micro' : ['small'],
}
