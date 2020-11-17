from bus import Bus
from processor import Processor
from request import Request
from cache_entry import CacheEntry

class MSI_Cache:
    def __init__(self, id, cacheSz, blockSz, a, bus, processor):
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

        # Stats related fields
        self.numReadMiss = 0
        self.numWriteMiss = 0
        self.numReadHit = 0
        self.numWriteHit = 0
        self.numBusTransaction = 0  

    def containsEntry(self, addr):
        tag, set_id = (addr % self.blockSz) // self.num_sets, (addr % self.blockSz) % self.num_sets
        begin = set_id * self.num_entries_per_set
        end = (set_id+1) * self.num_entries_per_set
        for i in range(begin, end):
            if self.entries[i].valid and self.entries[i].tag == tag:
                return i
        return -1
    
    def addEntry(self, entry):
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
            writeBackRequest = Request(None, 'Flush', self.id)
            self.bus.requests.append(writeBackRequest)

    # Need to modify according to protocol
    def snoopBus(self, clock):
        if self.bus.currentData != None:
            request = self.bus.currentData
            entry_id = self.containsEntry(request.addr)
            if request.msg == 'Flush':
                print('Bus is performing flush request')
                return 'UNUSED'
            if entry_id != -1:
                entry = self.entries[entry_id]
                # State must be M or S
                if not(request.response) and request.msg == 'BusRd':
                    if entry.state == 'S':
                        entry.access = clock
                        pass
                    elif entry.state == 'M':
                        writeBackRequest = Request(request.addr, 'Flush', self.id)
                        self.bus.requests.append(writeBackRequest)
                        entry.access = clock
                        entry.state = 'S'    
                    else:
                        print("snoopBus: Incorrect state while snooping")
                        exit()
                    request.response = True
                    self.bus.currentData = request
                    self.bus.currentData.entry = entry
                    self.entries[entry_id] = entry
                    print(f'Cache {self.id} performed bus request for msg {request.msg}')
                    return 'BusRd'
                elif request.msg == 'BusRdX' and request.coreId != self.id:
                    entry.valid = False
                    request.response = True
                    self.bus.currentData = request
                    self.entries[entry_id] = entry
                    print(f'Cache {self.id} performed bus request for msg {request.msg}')
                    return 'BusRdX'
                elif request.msg == 'BusUpgr' and request.coreId != self.id:
                    entry.valid = False
                    request.response = True
                    self.bus.currentData = request
                    self.entries[entry_id] = entry
                    print(f'Cache {self.id} performed bus request for msg {request.msg}')
                    return 'BusUpgr'
                elif (request.msg in ['BusRdX', 'BusUpgr'] and request.coreId == self.id) or request.response:
                    pass
                else:
                    print(f'Wrong msg {request.msg}, {request.coreId} detected in the bus while snooping by cache {self.id}')
            return 'UNUSED'
        elif self.bus.reply != None:
            request = self.bus.reply
            if self.bus.reply.coreId == self.id and self.bus.reply.addr == self.currentRequestAddr:
                entry_id = self.containsEntry(request.addr)
                if self.bus.reply.response:
                    if entry_id != -1:
                        self.entries[entry_id].state = 'S' if self.currentRequestType == 'READ' else 'M'  # Relying on python's mutable objects
                        self.entries[entry_id].access = clock # Relying on python's mutable objects
                    else:
                        newEntry = CacheEntry()
                        if self.bus.reply.entry != None:
                            newEntry = self.bus.reply.entry
                        else:
                            newEntry.access = clock
                            newEntry.valid, newEntry.tag, newEntry.index = True, (request.addr % self.blockSz) // self.num_sets, (request.addr % self.blockSz) % self.num_sets
                        newEntry.state = 'S' if self.currentRequestType == 'READ' else 'M'
                        self.addEntry(newEntry)
                    return 'RECV_DATA'

        return 'UNUSED'

    def tick(self, clock):
        res = self.snoopBus(clock)
        # print(f'{res} returned by snooping at cache {self.id}')
        if res not in ['UNUSED', 'RECV_DATA']:
            return
        elif res == 'RECV_DATA':
            print(f'Cache {self.id} received data from bus transaction')
            self.processor.response = self.currentRequestAddr
            self.currentRequestAddr = None
            self.currentRequestType = None
            return
        elif self.currentRequestAddr == None and self.processor.requestAddr != None:
            self.currentRequestAddr = self.processor.requestAddr
            self.currentRequestType = self.processor.requestType

            if self.currentRequestType == 'READ':
                entry_id = self.containsEntry(self.currentRequestAddr)
                if entry_id != -1 and self.entries[entry_id].state in ['M', 'S']:
                    print(f'Read hit at cache {self.id} in {self.entries[entry_id].state} state')
                    self.processor.response = self.currentRequestAddr
                    self.currentRequestAddr = None
                    self.entries[entry_id].access = clock  # Relying on python's mutable objects
                else:
                    print(f'Read miss at cache {self.id}')
                    request = Request(self.currentRequestAddr, 'BusRd', self.id)
                    self.bus.requests.append(request)
            if self.currentRequestType == 'WRITE':
                entry_id = self.containsEntry(self.currentRequestAddr)
                if entry_id != -1 and self.entries[entry_id].state == 'M':
                    print(f'Write hit at cache {self.id} in M state')
                    self.processor.response = self.currentRequestAddr
                    self.currentRequestAddr = None
                    self.entries[entry_id].access = clock  # Relying on python's mutable objects
                elif entry_id != -1 and self.entries[entry_id].state == 'S':
                    print(f'Write hit at cache {self.id} in S state')
                    self.processor.response = self.currentRequestAddr
                    request = Request(self.currentRequestAddr, 'BusUpgr', self.id)
                    self.currentRequestAddr = None
                    self.bus.requests.append(request)
                    self.entries[entry_id].access = clock  # Relying on python's mutable objects
                    self.entries[entry_id].state = 'M'  # Relying on python's mutable objects
                else:
                    print(f'Write miss at cache {self.id}')
                    request = Request(self.currentRequestAddr, 'BusRdX', self.id)
                    self.bus.requests.append(request)
        else: # do nothing
            pass
        return