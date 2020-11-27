# A bus is a path where all the requests are made
# It carries some data which can be request or response

# Request-reply cycle
# Request -> Reply -> Request till reply becomes None
# Once no reply move to next request in the queue

class Bus:
    def __init__(self):
        self.requests = []
        self.currentData = None
        self.reply = None
        self.done = False
    
    # i) Start a request on the bus
    # ii) Put a reply on the bus
    def tick(self, clock):
        if self.reply == None:
            if self.requests:
                self.currentData = self.requests[0]
                self.requests = self.requests[1:]
                self.reply = None
            else:
                self.done = True
                return
        else:
            self.currentData = self.reply
            self.reply = None
    
    def dump(self):
        if self.currentData != None:
            print('-'*18 + ' Bus State ' + '-'*18)
            self.currentData.dump()
            print('\n')
        elif self.reply != None:
            print('-'*18 + ' Bus State ' + '-'*18)
            self.reply.dump()
            print('\n')