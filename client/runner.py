#! /usr/bin/env python
import os, argparse
from scenarios import *
from cloud.instances import *
from testplan import *

import sys
import subprocess,re
from ab import ApacheBench

individual_dir = './individual'

def setup_dirs():
    if not os.path.isdir(individual_dir):
        os.mkdir(individual_dir)

def print_header():
    print
    print "===================[ GeoTrellis Cloud Benchmark ]==================="
    print

def log(msg,tier=0):
    print "[CLOUD]  %s%s" % ('\t'*tier,msg)

def run_individual_ec2(server):
    this_req = req
    this_concur = concur
    this_sizes = None
    if server in server_params:
        (this_req,this_concur) = server_params[server]
    if server in server_raster_sizes:
        this_sizes = server_raster_sizes[server]

    print " == %s == " % server
    if this_sizes:
        for s in this_sizes:
            runab.run(this_req,this_concur,ec2_servers[server],
                      os.path.join(individual_dir,'%s.%s.csv' % (server,s)),s)            
    else:
            runab.run(this_req,this_concur,ec2_servers[server],
                      os.path.join(individual_dir,'%s.csv' % server)) 

def run_rackspace(servers):
    pass

def run_micros():
    print 
    print "[GTBC]  === Running against micro instances. === "
    print
    print "[GTBC] Running against Amazon..."
    run_individual_ec2('t1.micro','small')
    print
    print "[GTBC] Running against Rackspace..."
    run_individual_rackspace('512MB','small')
    print
    print "[GTBC] Done."

def run_lb_micros():
    print 
    print "[GTBC]  === Running against load balanced micro instances. === "
    print
    print "[GTBC] Running against Amazon..."
    run_individual_ec2('t1.micro')
    print
    print "[GTBC] Running against Rackspace..."
    run_individual_rackspace('512MB')
    print
    print "[GTBC] Done."

def check_server(server):
    import urllib2
    addr = "http://%s/test" % server
    try:
        urllib2.urlopen(addr, timeout=3).read()
    except(IOError):
        return False
    return True

def warmup(server):
    ApacheBench.run(5,2,Scenario.warmup_scenario().addr(server))

def hs(args):
    scenarios = []
    for size in args.sizes:
        scenarios.append(HillshadeScenario(args.servertype,size,args.response,args.times,
                                           args.storage,args.concurrent,args.requests,args.concur))
    return scenarios

def wo(args):
    scenarios = []
    for size in args.sizes:
        scenarios.append(OverlayScenario(args.servertype,size,args.response,args.storage,args.requests,args.concur))
    return scenarios

def usace(args):
    if args.block:
        return [UsaceScenario(args.servertype,'block', args.requests,args.concur)]
    else:
        return [UsaceScenario(args.servertype,'local', args.requests,args.concur)]

def mergedict(d1,d2):
    #Values are lists.
    d = {}
    k1 = set(d1)
    k2 = set(d2)
    for k in (k1 & k2):
        d[k] = d1[k] + d2[k]
    for k in (k1 - k2):
        d[k] = d1[k]
    for k in (k2 - k1):
        d[k] = d2[k]
    return d

def mergedicts(*args):
    reduce(lambda d1,d2: mergedict(d1,d2), args)

def testplan(args):
    test_plan = None
    print args.only
    if args.only:
        if args.only == 'wo':
            test_plan = test_wo()
        elif args.only == 'hs':
            test_plan = test_hs()
        elif args.only == 'lb':
            test_plan = test_lb()
        elif args.only == 'nlb':
            test_plan = mergedict(test_wo(),test_hs())
        elif args.only == 'vs':
            test_plan = test_hp_vs_amazon()
    else:
        test_plan = mergedicts(test_wo(),test_hs(),test_lb())

    log("RUNNING TEST PLAN")
    if args.only:
        log("(Running only %s)" % args.only)
    results = []
    for server in test_plan:
        log("Running all scenarios against %s" % server)
        results = results + run_scenarios(server, test_plan[server])
    return results

class Result:
    def __init__(self,ab_result,scenario,addr):
        self.ab_result = ab_result
        self.scenario = scenario
        self.addr = addr

def run_scenarios(server,scenarios):
    print_header()
    log("Checking connectivity to %s..." % server)
    if not check_server(server):
        log("ERROR: Server %s does not exist or is not running." % server)
        return []

    log("Warming up server...")
    try:
        warmup(server)
    except:
        log("Warming up failed, trying again...",1)
        warmup(server)
    log("Done.",1)


    log("Running %s scenario(s) against %s" % (len(scenarios),server))

    results = []
    try:
        for scenario in scenarios:
            log(" = " + str(scenario) + " = ")
            addr = scenario.addr(server)
            log("Beginning run (%s)..." % addr,1)
            try:
                result = ApacheBench.run(scenario.requests,scenario.concurrency,addr)
                results.append(Result(result,scenario,addr))
            except:
                log("Apache Bench failed, trying again...",1)
                result = ApacheBench.run(scenario.requests,scenario.concurrency,addr)
                log("Done. Took %s seconds." % (result['Total Time (s)']),1)
                results.append(Result(result,scenario,addr))
    except:
        log("[ERROR!] Exception thrown")

    for r in filter(lambda r: r.ab_result['error'],list(results)):
        results.remove(r)
        log("[ERROR]   Test Failed for %s at %s" % (r.scenario,r.addr))

    log("%d Scenarios run successfully.\n" % len(results))

    return results

def write_results(results,path):
    log("Writing results to %s..." % path)
    keys = ApacheBench.fields.keys()
    txt = ''
    if not os.path.isfile(path):
        l = map( lambda x:'"' +  x + '"', keys)
        txt += '"Server Type","Storage Type","Response Type","Test Name","Custom","Req/Connections","Connections",' 
        txt += reduce(lambda x,y: x+','+y, l)
        txt += ',"URL"\n'
    for result in results:
        txt += '"%s","%s","%s","%s","%s","%d","%d",' % (result.scenario.servertype,
                                                        result.scenario.storage,
                                                        result.scenario.response_type,
                                                        result.scenario.testname,
                                                        result.scenario.custom,
                                                        result.scenario.requests,
                                                        result.scenario.concurrency)
        txt += reduce(lambda x,y: x + ',' + y, map(lambda x: '"' + result.ab_result[x] + '"', keys))
        txt += ',"%s"\n' % (result.addr)
            
    open(path,'a').write(txt)

def run(args):
    if not args.out:
        args.out = get_file_name(args)

    results = None
    if args.command == 'testplan':
        results = testplan(args)
    else:
        scenarios = args.func(args)
        results = run_scenarios(args.server,scenarios)

    write_results(results,args.out)

    print
    return 0

class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.stderr.write('\nERROR: %s\n\n' % message)
        sys.exit(2)

class ServerAction(argparse.Action):
    def __call__(self,parser,args,values,option_string=None):
        running = filter(lambda ins: ins.instance_type == values, EC2Instances().running())
        setattr(args,'servertype',values)
        if running:
            setattr(args,self.dest,running[0].public_dns_name + ':8000')
        else:
            setattr(args,self.dest,values)

class SizeAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        if values == 'all':
            setattr(args,self.dest,Scenario.dimensions.keys())
        else:
            setattr(args,self.dest,[values])

if __name__ == "__main__":
    def add_default_args(parser):
        parser.add_argument('-r','--requests',dest='requests', metavar='REQUESTS', type=int, default = 500,
                            help='Number of requests to make per concurrent requester.')
        parser.add_argument('-c','--concurrency',dest='concur', metavar='CONCURRENCY', type=int, default = 5,
                            help='Number of concurrent requesters.')
        parser.add_argument('-o','--output',dest='out', metavar='OUTPUT_FILE', default='results.csv',
                            help='Path for output csv file. Defaults to value calculated for scenario.')
        parser.add_argument('-n','--nopng',dest='response', action='store_false', default=True,
                            help='Set to not have server respond with a png')
        parser.add_argument('server', metavar='SERVER:PORT', action=ServerAction,
                            help='Server to connect to (e.g. localhost:8000)')
    
    root_parser = Parser(description='Runs the GeoTrellis cloud platform benchmark.')

    subparsers = root_parser.add_subparsers(title='Subcommands',
                                       description='Choose which scenario to run.',
                                       dest='command')

    hs_parser = subparsers.add_parser('hs', help='Hillshade benchmark test.')
    add_default_args(hs_parser)

    hs_parser.add_argument('-t','--times',dest='times', metavar='SIZE', type=int, default=2,
                   help='Times to run hillshade operation.')
    hs_parser.add_argument('-x','--concurrent',dest='concurrent',action='store_true',
                   help='If set, hillshade will run in concurrent mode.')

    hs_parser.add_argument('-s','--size',dest='sizes', metavar='SIZE', default = Scenario.dimensions.keys(), 
                        action=SizeAction,
                        choices = Scenario.dimensions.keys() + ['all'],
                        help='Size of the rasters to test across io stores.')
    hs_parser.add_argument('-i','--io',dest='storage', metavar='IO', default = 'cache',
                        choices=Scenario.storages,
                        help='IO Store to test across sizes.')
    hs_parser.set_defaults(func=hs)



    wo_parser = subparsers.add_parser('wo', help = 'Weighted Overlay benchmark test.')
    add_default_args(wo_parser)
    wo_parser.add_argument('-s','--size',dest='sizes', metavar='SIZE', default = Scenario.dimensions.keys(), 
                        action=SizeAction,
                        choices = Scenario.dimensions.keys() + ['all'],
                        help='Size of the rasters to test across io stores.')
    wo_parser.add_argument('-i','--io',dest='storage', metavar='IO', default = 'cache',
                        choices=Scenario.storages,
                        help='IO Store to test across sizes.')

    wo_parser.set_defaults(func=wo)

    usace_parser = subparsers.add_parser('usace', help = 'Usace benchmark test.')
    add_default_args(usace_parser)
    usace_parser.add_argument('-b','--block',dest='block',action='store_true',
                              help="Use block storage as opposed to local storage.")
    usace_parser.set_defaults(func=usace)

    testplan_parser = subparsers.add_parser('testplan', help = 'Testplan benchmark test.')
    testplan_parser.add_argument('-t','--testonly',dest='only',choices=['wo','hs','lb','nlb','vs'],
                                 help="Only test one subsection of test plan")
    testplan_parser.add_argument('-o','--output',dest='out', metavar='OUTPUT_FILE', default='results.csv',
                            help='Path for output csv file. Defaults to value calculated for scenario.')
    testplan_parser.set_defaults(func=testplan)
    
    exit(run(root_parser.parse_args()))
