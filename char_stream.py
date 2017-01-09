from stream import stream

class char_stream(stream):
    self.line,  self.col = 0, 0

    def next(self):
        ch = self._stream[pos]
        self.col = self.col + 1
        if ch == '\n':
            col = 0
            self.line = self.line + 1
        self.pos = self.pos + 1
        return ch

    def croack(self, msg):
        return "Error: %d line %d col"%(line,col)
