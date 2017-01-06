


class stream():
    
    def __init__(self, lst, pos=0):
        self._stream = lst
        self.pos = pos

    def lookahead(self):
        return self._stream[self.pos - 1]

    def peek(self):
        return self._stream[self.pos]

    def next(self):
        pos = pos + 1
        return self.lookahead()

    def eof(self):
        return self.pos >= len(self._stream)

    def looknext(self):
        return self._stream[self.pos + 1]

    def leftnum(self):
        return len(self._stream) - self.pos
