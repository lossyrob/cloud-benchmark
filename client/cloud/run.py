#! /usr/bin/env python

import argparse
from subprocess import call
from instances import EC2Instances
import enum

def check_server(server):
    import urllib2
    addr = "http://%s:8000/test" % server
    try:
        urllib2.urlopen(addr, timeout=5).read()
    except:
        return False
    return True

def create(typ):
    instances = EC2Instances()
    r = instances.start(typ)
    print "Created %s" % r.instances[0].public_dns_name

def do_run(args):
    instances = EC2Instances()
    not_started = filter(lambda s: not check_server(s.public_dns_name),instances.running())
    if not not_started:
        print
        print "ALL INSTANCES STARTED RUNNING INSTANCES"
        print
        return

    for x in not_started:
        print "Starting %s (%s)..." % (x.public_dns_name,x.instance_type)
        call(["/home/rob/tmp/gtcb/dosetup.sh " + x.public_dns_name + " &"],shell=True)
        print "Done."
    print    
    
def create_command(args):
    create(args.typ)

def prices(args):
    print
    print "INSTANCE TYPE\t\tPRICE PER HOUR"
    print "-------------\t\t---------------"
    for x in enum.server_info['Amazon']:
        print "%s\t\t$%f" % (x, enum.server_info['Amazon'][x][3])
    print    

def list_running(args):
    instances = EC2Instances()
    running = instances.running()
    if not running:
        print
        print "NO RUNNING INSTANCES"
        print
        return

    print
    print "INSTANCE TYPE\t\tPUBLIC DNS NAME\t\t\t\t\tSTARTED?"
    print "-------------\t\t---------------\t\t\t\t\t---"
    for x in running:
        print "%s\t\t%s\t\t%s" % (x.instance_type, x.public_dns_name,str(check_server(x.public_dns_name)))
    print
    

if __name__ == '__main__':
    root_parser = argparse.ArgumentParser(description='Sets up EC2 instances for benchmark running.')

    subparsers = root_parser.add_subparsers(title='Commands')

    create_parser = subparsers.add_parser('create', help='Creates an EC2 instance.')
    create_parser.add_argument('typ', metavar='TYPE',
                            help='Instance type')

    create_parser.set_defaults(func=create_command)

    list_parser = subparsers.add_parser('list', help='Lists all running EC2 instance.')
    list_parser.set_defaults(func=list_running)

    prices_parser = subparsers.add_parser('prices', help='Lists prices for EC2 instances.')
    prices_parser.set_defaults(func=prices)

    start_parser = subparsers.add_parser('start', help='Start unstarted EC2 instances.')
    start_parser.set_defaults(func=do_run)

    
    args = root_parser.parse_args()
    args.func(args)
