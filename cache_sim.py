import random
from moesi_cache import MOESI_Cache, Processor, Bus
from memory import RAM
random.seed(305)

# Note: Need to verify that the objects are copied where necessary
# Else mutation can occur and all sorts of crazy bugs will occur

class Computer:
    def __init__(self, n, instructions, cacheSz, blockSz, a):
        self.bus = Bus()
        self.mem = RAM(self.bus)
        self.n = n
        self.processors = [Processor(i, instructions[i]) for i in range(n)]
        self.caches = [MOESI_Cache(i, cacheSz, blockSz, a, self.bus, self.processors[i]) for i in range(n)]
        self.globalClock = 0
        self.done = False
    def run(self):
        maxTime = 20
        while not(self.done) and self.globalClock < maxTime:
            print('#'*18 + ' ' + str(self.globalClock) + ' ' + '#'*18)

            for p in self.processors:
                p.tick(self.globalClock)
            random.shuffle(self.caches)
            for c in self.caches:
                c.tick(self.globalClock)
            
            self.mem.tick(self.globalClock)
            
            self.bus.tick(self.globalClock)
            
            self.dump()

            for p in self.processors:
                p.tock(self.globalClock)
            self.globalClock += 1
            self.done = True
            for p in self.processors:
                if not(p.done):
                    self.done = False
            # self.done = self.done and self.bus.done
        efficiency = 0
        for p in self.processors:
            efficiency += 1-p.wastedCycles/p.numCycles
            print(f'Processor {p.id}: Total cycles = {p.numCycles}, Useful cycles = {p.numCycles-p.wastedCycles}, Efficiency = {1-p.wastedCycles/p.numCycles}')
        print(f'Total efficieny = {efficiency/self.n}')
    
    def dump(self):
        self.bus.dump()
        for c in self.caches:
            c.dump()

if __name__ == '__main__':
    # Test 1
    cs,bs,a,n,instructions = 64,16,1,2,[[['READ', 16], ['WRITE',16], ['READ',16]], [['WRITE', 16], ['READ',16], ['WRITE',16]]]
    # Test 2
    # cs,bs,a,n,instructions = 64,16,1,2,[[['WRITE', 16], ['READ',16]], [['READ',16], ['READ',16]]]
    cs,bs,a,n,instructions = 64,16,1,2,[[['READ', 16], ['WRITE',16]], [['READ', 43], ['WRITE',43]]]
    comp = Computer(n,instructions, cs, bs, a)
    comp.run()