class CacheEntry:
    def __init__(self):
        self.tag = None
        self.valid = False
        self.index = None
        self.state = None
        self.access = None
    
    def dump(self):
        print('{}\t{}\t{}\t{}\t{}'.format(self.valid, self.tag, self.index, self.state, self.access))