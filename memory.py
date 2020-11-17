MEM_ACCESS_TIME = 4
class RAM:

    def __init__(self, bus):
        self.bus = bus
    
    def tick(self, clock):
        if self.bus.currentData != None and self.bus.reply == None:
            self.bus.reply = self.bus.currentData
            self.bus.currentData = None
            self.bus.reply.responseTime += 1
            if self.bus.reply.responseTime == MEM_ACCESS_TIME:
                self.bus.reply.response = True      # if request was not to flush, it must have been some data request
                if self.bus.reply.msg == 'Flush':
                    self.bus.reply = None        # if request was to flush, once completed no reply is expected