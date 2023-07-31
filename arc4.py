#!/usr/bin/python
#
# This code was copied from the Wikipedia entry for RC4. Copyright status unknown.
#

class ARC4:
    def __init__(self, key = None):
        self.state = range(256) # Initialize state array with values 0 .. 255
        self.x = self.y = 0 # Our indexes. x, y instead of i, j
        
        if key is not None:
            self.init(key)
            pass
        return
    
    # KSA
    def init(self, key):
        for i in range(256):
            self.x = (ord(key[i % len(key)]) + self.state[i] + self.x) & 0xFF
            self.state[i], self.state[self.x] = self.state[self.x], self.state[i]
            pass
        self.x = 0
        return
    
    # PRGA
    def crypt(self, input):
        output = [None]*len(input)
        for i in xrange(len(input)):
            self.x = (self.x + 1) & 0xFF
            self.y = (self.state[self.x] + self.y) & 0xFF
            self.state[self.x], self.state[self.y] = self.state[self.y], self.state[self.x]
            r = self.state[(self.state[self.x] + self.state[self.y]) & 0xFF]
            output[i] = chr(ord(input[i]) ^ r)
            pass
        return ''.join(output)
    pass

if __name__ == '__main__':
    test_vectors = [['Key', 'Plaintext'], 
                    ['Wiki', 'pedia'], 
                    ['Secret', 'Attack at dawn']]
    
    for i in test_vectors:
        print(ARC4(i[0]).crypt(i[1]).encode('hex').upper())
        pass
    pass
