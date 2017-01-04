from buildin_operators import operators, op_order, Binary, Unary

keywords = {
'and': 'AND',
'or' : 'OR'，
'not': 'NOT',
'def': 'DEF',
'lambda': 'LAMBDA',
'if': 'IF',
'else': 'ELSE',
'True': 'TRUE',
'False': 'FALSE',
'end': 'END',

}

escape = {
    'n' : '\n',
    'r' : '\r',
    't' : '\t',
    '\\' : '\\',
    'a' : '\a',
    '"' : '"',
    'v' : '\v',
    'f' : '\f',
    'b' : '\b',
}

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

class token():
    
    def __init__(self, inputstream):
        self.inputstream = inputstream
        self.token_list = []
        self.pos = 0


    def read_tokens(self):
        token_list = [None]
        while True:
            tkn = read_a_token()
            if tkn is None:
                return token_list
            token_list.append(tkn)
        
    def read_a_token(self):
        self.read_white_space()
        if self.inputstream.eof(): return None
        ch = self.inputstream.peek()
        if ch == '"': tkn = self.read_string()
        elif ch == '[': tkn = self.read_list()
        elif ch == '{': tkn = self.read_hashmap()
        elif ch == '(': tkn = self.read_parn()
        elif ch == '.': tkn = self.read_dot()
        elif str.isdigit(ch): tkn = self.read_num()
        elif str.isalpha(ch): tkn = self.read_var()
        elif ch in ',\n':     tkn = self.read_sep()
        else: tkn = self.read_op()   # throw exception
        return tkn

    def read_sep(self):
        ch = self.inputstream.peek()
        if ch == ',': return ('SEP', 'COMMA')
        else: return ('SEP', 'NEWLINE')
        
    def read_white_space(self, ss = " \t"):
        if self.inputstream.eof(): return None
        while self.inputstream.peek() in ss:
            self.inputstream.next()

    def read_var(self):
        var = ""
        while str.isalnum(self.inputstream.peek()):
            var += self.inputstream.next()
        if var in keywords:
            return (keywords[var], var)
        return ("VAR", var)
        
    def read_op(self):
        TYPE = 'OP'
        op = ""
        while self.inputstream.peek() in '!=<>|$&:_@%':
            var += self.inputstream.next()
        if op in operators: 
            return (TYPE, operators[var])
        else:
            self.inputstream.croak('invalid syntax')

    def read_pair(self, TYPE, end_ch):
        val = []
        self.inputstream.next()
        while not self.inputstream.eof():
            self.read_white_space()
            ch = self.inputstream.peek()
            if ch == end_ch:
                self.inputstream.next()
                return (TYPE, val)
            else:
                val.append(self.read_a_token())

        self.inputstream.croak('missing ' + end_ch)

    def read_list(self):
        return self.read_pair('LIST', ']')

    def read_hashmap(self):
        return self.read_pair('MAP', '}')

    def read_parn(self):
        return self.read_pair('PARN', ']')

    def read_num(self):
        TYPE = 'NUM'
        ns = ""
        has_e = False
        while True:
            ch = self.inputstream.next()
            if str.isdigit(ch) or ch =='.':
                ns += ch
                has_e = False
            else if ch == 'E' or ch == 'e':
                ns += ch
                has_e = True
            else if has_e and (ch == '+' or ch == '-'):
                ns += ch
                has_e = False
            else:
                return (TYPE , self.num(ns))

    def read_dot(self):
        if str.isdigit(self.inputstream.looknext()): return self.read_num()
        else: return ('DOT', '.')

    def read_string(self):
        val = ""
        TYPE = 'STRING'
        self.inputstream.next()
        while not self.inputstream.eof():
            ch = self.inputstream.next()
            if ch == '\n':
                self.inputstream.croak('missing "')
                return ('ERROR', "")
            elif isEscape:
                isEscape = False
                if ch in escape_table:
                    val += escape_table[ch]
                else:
                    val += "\\" + ch
            elif ch == '\\':
                isEscape = True
            else if ch == '"':
                return (TYPE, val)
            else:
                val += ch

        self.inputstream.croak('missing "')
