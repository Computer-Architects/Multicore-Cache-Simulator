from bus import Bus
from processor import Processor
from request import Request
from cache_entry import CacheEntry
from copy import deepcopy

class MSI_Cache:
    """
    Simulator for the MSI cache with the processor

    ...
    Methods
    -------
    containsEntry(addr:int)
    addEntry(entry: CacheEntry)
    snoopBus(clock:int)
    tick( clock:int)
    dump()
    """
    def __init__(self, id, cacheSz, blockSz, a, bus, processor):
        """ Constructor for the class

        ...
        Parameters
        ----------
        id: int
            id of the processor
        cacheSz: int
             size of the cache
        blockSz: int
            size of the block
        a: int
            Associativity
        bus: Bus
            bus object
        processor: Processor
            processor object
        """
        self.id = id
        self.num_entries = int(cacheSz / blockSz)
        self.entries = [CacheEntry() for i in range(self.num_entries)]
        self.cacheSz = cacheSz
        self.blockSz = blockSz
        self.num_sets = self.num_entries // a
        self.num_entries_per_set = self.num_entries // self.num_sets
        self.a = a
        self.bus = bus
        self.processor = processor
        self.currentRequestAddr = None
        self.currentRequestType = None
        self.currentRequestId = None

        # Stats related fields
        self.cacheAccesses = 0
        self.cacheHits = 0
        self.cacheMisses = 0
        self.numMemBusTransaction = 0
        self.numCacheBusTransaction = 0  

    def containsEntry(self, addr):
        """Checks if the cache contains an entry as per the address

        ...
        Parameters
        ----------
        addr: int
            address in DM
        
        Returns
        ------
        int
            the appropriate index in cache, or -1 if not available
        """
        tag, set_id = (addr // self.blockSz) // self.num_sets, (addr // self.blockSz) % self.num_sets
        begin = set_id * self.num_entries_per_set
        end = (set_id+1) * self.num_entries_per_set
        for i in range(begin, end):
            if self.entries[i].valid and self.entries[i].tag == tag:
                return i
        return -1
    
    def addEntry(self, entry):
        """Add a new entry in cache using LRU

        Parameters
        ----------
        entry: int
            the new entry to be added in the cache
        """
        set_id = entry.index #(addr % self.blockSz) // self.num_sets, (addr % self.blockSz) % self.num_sets
        begin = set_id * self.num_entries_per_set
        end = (set_id+1) * self.num_entries_per_set
        for i in range(begin, end):
            if not(self.entries[i].valid):
                self.entries[i] = entry
                return
        # Implement LRU
        cur_access = self.entries[begin].access
        cur_id = begin
        for i in range(begin, end):
            if self.entries[i].access < cur_access:
                cur_id = i      
                return
        evict_entry = self.entries[cur_id]
        self.entries[cur_id] = entry
        if evict_entry.state == 'M':
            writeBackRequest = Request(None, 'Flush', self.id, self.currentRequestId)
            self.bus.requests = [writeBackRequest] + self.bus.requests
            self.numMemBusTransaction += 1

    # Need to modify according to protocol
    def snoopBus(self, clock):
        """Snoops the bus and updates accordingly

        .....
        Parameters
        ----------
        clock: int
            the clock tick number
        Returns
        -------
        str
            Action performed by cache on Snooping
        """
        if self.bus.currentData != None:
            request = deepcopy(self.bus.currentData)
            print(request.addr, request.coreId, request.msg, self.id, request.response)
            # entry_id = self.containsEntry(request.addr)

            if request.response or request.msg == 'Flush':
                # This is a response to some data request
                if request.addr != None and request.id == self.currentRequestId and request.coreId == self.id and request.addr == self.currentRequestAddr:
                    entry_id = self.containsEntry(request.addr)
                    if request.responseTime == 0:
                        self.numCacheBusTransaction += 1
                    if request.responseTime > 0 or request.msg == 'Flush':
                        self.numMemBusTransaction += 1
                    if request.response:
                        self.bus.currentData = None
                    if entry_id != -1:
                        self.entries[entry_id].state = 'S' if self.currentRequestType == 'READ' else 'M'  # Relying on python's mutable objects
                        self.entries[entry_id].access = clock # Relying on python's mutable objects
                    else:
                        newEntry = CacheEntry()
                        if request.entry != None:
                            newEntry = request.entry
                        else:
                            newEntry.access = clock
                            newEntry.valid, newEntry.tag, newEntry.index = True, (request.addr // self.blockSz) // self.num_sets, (request.addr // self.blockSz) % self.num_sets
                        newEntry.state = 'S' if self.currentRequestType == 'READ' else 'M'
                        self.addEntry(newEntry)

                    return 'RECV_DATA'
                
            else:
                entry_id = self.containsEntry(request.addr)
                if entry_id != -1:
                    entry = self.entries[entry_id]
                    # State must be M or S
                    if request.msg == 'BusRd':
                        if entry.state == 'S':
                            entry.access = clock
                            request.response = True
                            self.bus.reply = request
                            self.bus.reply.entry = entry
                            self.entries[entry_id] = entry
                        elif entry.state == 'M':
                            # writeBackRequest = Request(request.addr, 'Flush', self.id)
                            self.bus.reply = request
                            self.bus.reply.msg = 'Flush'
                            self.bus.reply.responseTime = 0
                            entry.access = clock
                            entry.state = 'S'    
                        else:
                            print("snoopBus: Incorrect state while snooping")
                            exit()
                        
                        print(f'Cache {self.id} performed bus request for msg {request.msg}')
                        return 'BusRd'

                    elif request.msg == 'BusRdX' and request.coreId != self.id:
                        # State is either 'M' or 'S'
                        entry.valid = False
                        # print(self.bus.currentData.response)
                        request.response = True
                        # print(self.bus.currentData.response)
                        self.bus.reply = request
                        self.entries[entry_id] = entry
                        print(f'Cache {self.id} performed bus request for msg {request.msg}')
                        return 'BusRdX'

                    elif request.msg in ['BusRdX'] and request.coreId == self.id:
                        pass

                    elif request.msg == 'BusUpgr' and request.coreId != self.id:
                        entry.valid = False
                        request.response = True
                        self.bus.reply = request
                        self.entries[entry_id] = entry
                        print(f'Cache {self.id} performed bus request for msg {request.msg}')
                        return 'BusUpgr'

                    elif request.msg == 'BusUpgr' and request.coreId == self.id:
                        # print(self.bus.currentData.response)
                        request.response = True
                        # print(self.bus.currentData.response)
                        self.bus.reply = request
                        return 'BusUpgr'

                    else:
                        print(f'Wrong msg {request.msg}, {request.coreId} detected in the bus while snooping by cache {self.id}')
        return 'UNUSED'

    def tick(self, clock):
        """Runs one tick of the clock

        .....
        Parameters
        ----------
        clock: int
            the clock tick number
        """
        res = self.snoopBus(clock)
        print(f'{res} returned by snooping at cache {self.id}')
        if res not in ['Upgraded', 'UNUSED', 'RECV_DATA']:
            return
        elif res == 'RECV_DATA':
            print(f'Cache {self.id} received data from bus transaction')
            self.processor.response = self.currentRequestAddr
            self.currentRequestAddr = None
            self.currentRequestType = None
            return
        elif res == 'Upgraded':
            print(f'Cache {self.id} upgraded an entry')
            self.processor.response = self.currentRequestAddr
            self.currentRequestAddr = None
            self.currentRequestType = None
            return
        elif self.currentRequestAddr == None and self.processor.requestAddr != None:
            self.currentRequestAddr = self.processor.requestAddr
            self.currentRequestType = self.processor.requestType
            self.currentRequestId = self.processor.requestId

            if self.currentRequestType == 'READ':
                entry_id = self.containsEntry(self.currentRequestAddr)
                if entry_id != -1 and self.entries[entry_id].state in ['M', 'S']:
                    self.cacheHits += 1
                    print(f'Read hit at cache {self.id} in {self.entries[entry_id].state} state')
                    self.processor.response = self.currentRequestAddr
                    self.currentRequestAddr = None
                    self.entries[entry_id].access = clock  # Relying on python's mutable objects
                else:
                    print(f'Read miss at cache {self.id}')
                    self.cacheMisses +=1 
                    request = Request(self.currentRequestAddr, 'BusRd', self.id, self.currentRequestId)
                    self.bus.requests.append(request)
            if self.currentRequestType == 'WRITE':
                entry_id = self.containsEntry(self.currentRequestAddr)
                if entry_id != -1 and self.entries[entry_id].state == 'M':
                    print(f'Write hit at cache {self.id} in M state')
                    self.cacheHits += 1
                    self.processor.response = self.currentRequestAddr
                    self.currentRequestAddr = None
                    self.entries[entry_id].access = clock  # Relying on python's mutable objects
                elif entry_id != -1 and self.entries[entry_id].state == 'S':
                    print(f'Write hit at cache {self.id} in S state')
                    self.cacheHits += 1
                    # self.processor.response = self.currentRequestAddr
                    request = Request(self.currentRequestAddr, 'BusUpgr', self.id, self.currentRequestId)
                    # self.currentRequestAddr = None
                    self.bus.requests.append(request)
                    self.entries[entry_id].access = clock  # Relying on python's mutable objects
                    # self.entries[entry_id].state = 'M'  # Relying on python's mutable objects
                else:
                    print(f'Write miss at cache {self.id}')
                    self.cacheMisses += 1
                    request = Request(self.currentRequestAddr, 'BusRdX', self.id, self.currentRequestId)
                    self.bus.requests.append(request)
        else: # do nothing
            pass
        return
    
    def dump(self):
        print('-'*18 + f' Cache {self.id} State ' + '-'*18)
        print(f"Statistics: Hits: {self.cacheHits} | Misses: {self.cacheMisses} | Number of cache-bus transactions:{self.numCacheBusTransaction} | Number of memory bus transactions: {self.numMemBusTransaction}")
        print('Valid\tTag\tIndex\tState\tLast Access time')
        for entry in self.entries:
            entry.dump()