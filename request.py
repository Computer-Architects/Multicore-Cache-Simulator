# A request constains fields- 
# i) memory address
# ii) Message (whether its a data request, msg to invalidate, etc)
# iii) CoreId (which core made the request)
# iv) response (indicated if data is present in some other cache)
# v) entry (cache entry received as response)
# vi) responseTime (since how long it has occupied the bus)
class Request:
    def __init__(self, addr, msg, coreId, id, response=False, entry=None):
        self.addr = addr
        self.msg = msg
        self.coreId = coreId
        self.response = response
        self.entry = entry
        self.responseTime = 0
        self.id = id
    
    def dump(self):
        if self.response:
            print(f'Response to request ({self.msg}, {self.addr}) from cache {self.coreId}')
        else:
            print(f'Request ({self.msg}, {self.addr}) from cache {self.coreId}, T = {self.responseTime}')