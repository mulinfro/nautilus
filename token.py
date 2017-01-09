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
'is' : 'IS',
'in' : 'IN',

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
    '\n': '',
}

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

class token():
    def __init__(self, tkn_type, tkn_val, line, col=0):
        self.tp   = tkn_type
        self.val  = tkn_val
        self.line = line
        self.col  = col

class token_stream():
    
    def __init__(self, stream):
        self.stream = stream
        self.token_list = []

    def read_tokens(self):
        token_list = [None]
        while True:
            tkn = read_a_token()
            if tkn is None:
                return token_list
            token_list.append(tkn)
        
    def read_a_token(self):
        self.read_white_space()
        if self.stream.eof(): return None
        ch = self.stream.peek()
        if ch in ('"', "'"): tkn = self.read_string()
        elif ch == '[': tkn = self.read_list()
        elif ch == '{': tkn = self.read_hashmap()
        elif ch == '(': tkn = self.read_parn()
        elif ch == '.': tkn = self.read_dot()
        elif ch == '$': tkn = self.read_sys_call()
        elif str.isdigit(ch): tkn = self.read_num()
        elif str.isalpha(ch) or ch == '_': tkn = self.read_var()
        elif ch in ',\n':     tkn = self.read_sep()
        elif ch is '\\':      tkn = self.link()
        else: tkn = self.read_op()   # throw exception
        return tkn

    def link(self):
        self.stream.next()
        if self.stream.next() != '\n':
            Error("unexpected char")
        else:
            return self.read_a_token()

    def read_sys_call(self):
        line, col = self.stream.line, self.stream.col
        self.stream.next()
        self.read_white_space()
        command = ""
        if self.stream.peek() == "'" and self.stream.looknext() == "'":
            command = self.read_multi_string()
            return token("SYSFUNC", command, line, col)
        else:
            while self.stream.peek() != '\n':
                command += self.stream.next()
            return token("SYSCALL", command, line, col)

    def read_sep(self):
        line, col = self.stream.line, self.stream.col
        ch = self.stream.next()
        if ch == ',':
            self.read_white_space(" \t\n")
            return token('SEP', 'COMMA', line, col)
        else: 
            return token('SEP', 'NEWLINE', line, col)
        
    def read_white_space(self, ss = " \t"):
        while not self.stream.eof() and self.stream.peek() in ss:
            self.stream.next()

    def read_var(self):
        line, col = self.stream.line, self.stream.col
        var = ""
        is_valid = lambda x: str.isalnum(x) or x == '_'
        while is_valid(self.stream.peek()):
            var += self.stream.next()
        if var in keywords:
            return (keywords[var], var)
        return token("VAR", var, line, col)
        
    def read_op(self):
        line, col = self.stream.line, self.stream.col
        op = ""
        while self.stream.peek() in '!=<>|$&:@%':
            var += self.stream.next()
        if op in operators: 
            return token("OP", operators[var], line, col)
        else:
            self.stream.croak('invalid syntax')

    def read_pair(self, end_ch):
        val = []
        self.stream.next()
        while not self.stream.eof():
            self.read_white_space(" \t\n")
            ch = self.stream.peek()
            if ch == end_ch:
                self.stream.next()
                return val
            else:
                val.append(self.read_a_token())

        self.stream.croak('missing ' + end_ch)

    def read_list(self):
        line, col = self.stream.line, self.stream.col
        val = self.read_pair(']')
        return token("LIST", val, line, col)

    def read_hashmap(self):
        line, col = self.stream.line, self.stream.col
        val = self.read_pair( '}')
        return token("MAP", val, line, col)

   # Q  may ( lambda x,y: x+ y)
    def read_parn(self):
        line, col = self.stream.line, self.stream.col
        val = self.read_pair(')')
        if ('SEP', 'COMMA') in val:
            return token('TUPLE', val, line, col)
        return token("PARN", val, line, col)

    def read_num(self):
        line, col = self.stream.line, self.stream.col
        ns = ""
        has_e = False
        while True:
            ch = self.stream.next()
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
                return token("NUM", num(ns), line, col)

    def read_dot(self):
        line, col = self.stream.line, self.stream.col
        if str.isdigit(self.stream.looknext()): return self.read_num()
        else: return token('DOT', '.', line, col)

    def check_multi_string(self, tc):
        if tc != self.stream.peek() or tc != self.stream.looknext():
            return False
        self.stream.next(), self.stream.next()
        return True

    def read_string(self):
        line, col = self.stream.line, self.stream.col
        val = ""
        terminal_char = self.stream.next()
        is_multi = self.check_multi_string(terminal_char)
        while not self.stream.eof():
            ch = self.stream.next()
            if isEscape:
                isEscape = False
                if ch in escape_table: val += escape_table[ch]
                else: val += "\\" + ch
            elif ch == '\n':
                self.stream.croak('missing %s'%terminal_char)
                #Error()
            elif ch == '\\':
                isEscape = True
            else if (ch == terminal_char) and (not is_multi \
                     or (self.check_multi_string(ch)) :
                return token('STRING', val, line, col)
            else:
                val += ch

        self.stream.croak('missing %s'%terminal_char)
