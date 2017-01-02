
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

operators = {
'|': 'PIPE',
'&>': 'WRITE',
'&>>': 'APPEND',
'+': 'ADD',
'*': 'MUL',
'/': 'DIV',
'-': 'MINUS',
'%': 'MOD',
'$': 'OSCALL',
'==': 'EQUAL',
'=': 'ASSINE',

}


class token():
    
    def __init__(self, inputstream):
        self.inputstream = inputstream
        self.token_list = []

    def read_tokens():
        token_list = []
        while True:
            tkn = read_a_token()
            if tkn is None:
                return token_list
            token_list.append(tkn)
        
    def read_a_token():
        self.read_white_space()
        if self.inputstream.eof(): return None
        ch = self.inputstream.peek()
        if ch == '"': tkn = self.read_string()
        else if ch == '[': tkn = self.read_list()
        else if ch == '{': tkn = self.read_hashmap()
        else if ch == '(': tkn = self.read_parn()
        else if ch == '.': tkn = self.read_dot()
        else if str.isdigit(ch): tkn = self.read_num()
        else if str.isalpha(ch): tkn = self.read_var()
        else: tkn = self.read_op()   # throw exception
        return tkn

    def read_white_space():
        ch = self.inputstream.peek()
        while ch == ' ' or ch == '\t' or ch == '\n': 
            self.inputstream.next()

    def read_var():
        var = ""
        while str.isalpha(self.inputstream.peek()):
            var += self.inputstream.next()
        return ("VAR", var)
        
    def read_op():
        TYPE = 'OP'
        op = ""
        while self.inputstream.peek() in '!=<>|$&':
            var += self.inputstream.next()
        if op in operators: 
            return (TYPE, operators[var])
        else:
            self.inputstream.croak('invalid syntax')

    def read_list():
        val = []
        TYPE = 'LIST'
        self.inputstream.next()
        need_sep = False
        while not self.inputstream.eof():
            self.read_white_space()
            ch = self.inputstream.peek()
            else if ch == ']':
                self.inputstream.next()
                return (TYPE, val)
            else if ch == ',':
                if need_sep: 
                    self.inputstream.next()
                    need_sep = False
                else:
                    self.inputstream.croak('invalid syntax')
            else:
                if not need_sep:
                    val.append(read_a_token())
                    need_sep = True
                else:
                    self.inputstream.croak('invalid syntax')

        self.inputstream.croak('missing ]')
        return ('ERROR', [])

    def read_num():
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


    def read_hashmap():
        val = []
        TYPE = 'MAP'
        self.inputstream.next()
        need_sep = False
        while not self.inputstream.eof():
            self.read_white_space()
            ch = self.inputstream.peek()
            else if ch == '}':
                self.inputstream.next()
                return (TYPE, val)
            else if ch == ',':
                if need_sep: 
                    self.inputstream.next()
                    need_sep = False
                else:
                    self.inputstream.croak('invalid syntax')
            else:
                if not need_sep:
                    key = read_a_token()
                    self.read_a_separator(':')
                    value = read_a_token()
                    val.append((key,value))
                    need_sep = True
                else:
                    self.inputstream.croak('invalid syntax')

    def read_parn():
        val = []
        TYPE = 'MAP'
        self.inputstream.next()
        is_tuple, need_sep = False, False
        while not self.inputstream.eof():
            self.read_white_space()
            ch = self.inputstream.peek()
            else if ch == ')':
                self.inputstream.next()
                return (TYPE, val)
            else if ch == ',':
                is_tuple = True
                if need_sep: 
                    self.inputstream.next()
                    need_sep = False
                else:
                    self.inputstream.croak('invalid syntax')
            else:
                if not (is_tuple and need_sep):
                    val.append(read_a_token)
                    need_sep = True
                else:
                    self.inputstream.croak('invalid syntax')

    def num(s):
        try:
            return int(s)
        except ValueError:
            return float(s)

    def read_a_separator(sep = ','):
        self.read_white_space()
        ch = self.inputstream.peek()
        if ch == sep:
            self.inputstream.next()
        else:
            self.inputstream.croak('unexpected seqarator ' + sep)

    def read_string():
        val = ""
        TYPE = 'STRING'
        self.inputstream.next()
        while not self.inputstream.eof():
            ch = self.inputstream.next()
            if ch == '\\':
                ch = self.inputstream.peek()
                if ch != '\n': val += ch
            else if ch == '\n':
                self.inputstream.croak('missing "')
                return ('ERROR', "")
            else if ch == '"':
                return (TYPE, val)
            else:
                val += ch
