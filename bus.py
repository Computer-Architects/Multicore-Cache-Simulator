MEM_ACCESS_TIME = 4
# A bus is a path where all the requests are made
# It carries some data which can be request or response

## To add: print current state ##
class Bus:
    def __init__(self):
        self.requests = []
        self.currentData = None
        self.reply = None
        self.done = False
    
    # i) Start a request on the bus
    # ii) Put a reply on the bus
    def tick(self, clock):
        if self.currentData == None or self.currentData.msg == 'BusUpgr':
            if self.requests:
                self.currentData = self.requests[0]
                self.requests = self.requests[1:]
                self.reply = None
            else:
                self.done = True
                return
        elif self.currentData.response:
            # Data is a reply
            assert self.reply == None
            self.reply = self.currentData
            self.currentData = None
        elif self.currentData.responseTime < MEM_ACCESS_TIME:
            self.currentData.responseTime += 1
            print(self.currentData.responseTime)
            if self.currentData.responseTime == MEM_ACCESS_TIME:
                if self.currentData.msg in ['BusRd', 'BusRdX']:
                    self.currentData.response = True
                elif self.currentData.msg == 'Flush':
                    self.currentData = None
        elif not(self.requests):
            self.done = True