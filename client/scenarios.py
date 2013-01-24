from collections import OrderedDict

class Scenario():
    dimensions = { 'small' : 256,
                   'med'   : 1408,
                   'big' : 2560 }

    storages = ['cache','local','block']

    # Defines a quick warm up scenario that will be run before
    # actual benchmarks are run.
    @staticmethod
    def warmup_scenario():
        return OverlayScenario('None','small',False,'cache',50,10)
    
    @staticmethod
    def get_name(size,storage,version = 1):
        return '%s_rast%d-%s' % (storage,version,size)

    def __init__(self,servertype,requests,concurrency,storage,response,custom,testname=''):
        self.servertype = servertype
        self.requests = requests
        self.concurrency = concurrency
        self.storage = storage
        self.response = response
        if response:
            self.response_type = "PNG"
        else:
            self.response_type = "Text"
        self.testname = testname
        self.custom = custom # custom key for output

    def addr(self, server):
        return "http://" + server + self.path

class OverlayScenario(Scenario):
    def __init__(self,servertype,size,response,storage = 'cache',requests = 500, concurrency = 5):
        self.dimension = Scenario.dimensions[size]
        custom = "%dx%d" % (self.dimension,self.dimension)
        Scenario.__init__(self,servertype,requests,concurrency,storage,response,custom,'Weighted Overlay')

        self.size = size
        rast1 = Scenario.get_name(size,storage,1)
        rast2 = Scenario.get_name(size,storage,2)
        self.path = '/wo/%s/%s/3/7/%s' % (rast1,rast2,str(response).lower())

    def __str__(self):
        s = "%s: Weighted Overlay on %s raster (%dx%d) in %s storage" % (self.servertype,
                                                                         self.size,
                                                                         self.dimension,self.dimension,
                                                                         self.storage)
        if self.response:
            s = s + " with PNG response."
        else:
            s = s + " with no PNG response."
        return s

    @staticmethod
    def enumerateAll(cls):
        for size in Scenario.dimensions:
            for response in [True,False]:
                for storage in Scenario.storages:
                    yield OverlayScenario(size,response,storage)

class HillshadeScenario(Scenario):
    def __init__(self,servertype,size,response,times,storage = 'cache',concurrent=False,requests = 500, concurrency = 5):
        self.dimension = Scenario.dimensions[size]
        custom = "%dx%d" % (self.dimension,self.dimension)
        Scenario.__init__(self,servertype,requests,concurrency,storage,response,custom,'Hillshade')

        self.size = size
        self.dimension = Scenario.dimensions[size]
        self.times = times
        self.concurrent = concurrent
        rast = Scenario.get_name(size,storage,1)
        self.path = '/hillshade'
        if concurrent:
            self.path += '-con'
        self.path += '/%s/%d/%s' % (rast,times,str(response).lower())
        
    def __str__(self):
        s = "%s: Hillshade on %s raster (%dx%d) in %s storage with %d times" % (self.servertype,
                                                                                self.size,
                                                                                self.dimension,
                                                                                self.dimension,
                                                                                self.storage,
                                                                                self.times)
        if self.concurrent:
            s += " (concurrent)"

        if self.response:
            s = s + " with PNG response."
        else:
            s = s + " with no PNG Response."
        return s

    @staticmethod
    def enumerateAll(cls):
        for size in Scenario.dimensions:
            for response in [True,False]:
                for storage in Scenario.storages:
                    for times in [1,2,4,8]:
                        for concurrent in [True,False]:
                            yield HillshadeScenario(size,response,times,storage,concurrent)

class UsaceScenario(Scenario):
    def __init__(self,servertype,storage = 'local',requests = 10, concurrency = 1):
        Scenario.__init__(self,servertype,requests,concurrency,storage,True,'','USACE Weighted Overlay')
        self.path = '/usace/%s' % storage

    def __str__(self):
        s = "%s: USACE Weighted Overlay in %s storage" % (self.servertype,self.storage)
        s = s + " with PNG response."
        return s

    @staticmethod
    def enumerateAll(cls):
        return [UsaceScenario('local'),UsaceScenario('block')]
