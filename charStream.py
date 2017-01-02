
class stream(s, is_file=False):
    pos,line,col = 0,0,0
    chars = s
    if is_file:
        with open(s) as f:
            chars = f.read()

    def peek():
        return chars[pos]

    def eof():
        return pos >= len(chars)

    def next():
        ch = chars[pos]
        col = col + 1
        if ch == '\n':
            col = 0
            line = line + 1
        pos = pos + 1
        return ch

    def croack(msg):
        return "Error: %d line %d col"%(line,col)
