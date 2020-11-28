class Processor():
    def __init__(self, id, instructions):
        self.requestAddr = None
        self.requestType = None
        self.requestId = 0
        self.instructions = instructions
        self.response = None
        self.done = False
        self.numCycles = 0
        self.wastedCycles = 0
        self.id = id
        
    def tick(self, clock):
        if not(self.done):
            self.numCycles += 1
        if self.requestAddr == None:
            if self.instructions:
                self.requestType = self.instructions[0][0]
                self.requestAddr = self.instructions[0][1]
                self.response = None
                self.instructions = self.instructions[1:]
    
    def tock(self, clock):
        if self.requestAddr != None:
            if self.response != None:
                self.requestAddr = None
                self.requestType = None
                self.requestId += 1
                if not(self.instructions):
                    self.done = True
            else:
                print(f'Processor {self.id} Waiting for response for {self.requestType} at {self.requestAddr} from cache ...')
                self.wastedCycles += 1