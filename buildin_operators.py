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
    '@': 'partial',
}

op_order = {
    '&>':1,
    '&>>':1,
    "=": 2,
    "||": 3,
    "&&": 4,
    "|": 5,
    "<": 7, ">": 7, "<=": 7, ">=": 7, "==": 7, "!=": 7,
    "+": 10, "-": 10,
    "*": 20, "/": 20, "%": 20,
}


_add = lambda x,y: x + y
_minus = lambda x,y: x - y    
_mul = lambda x,y: x * y    
_div = lambda x,y: x / y    
_mod = lambda x,y: x % y    
_equal = lambda x,y: x == y
_and = lambda x,y: x and y
_or = lambda x,y: x or y 
_not = lambda x: not x
_pipe = lambda x: f(x)

def _write_helper(var, filename, mode):
    var = str(var)
    with open(filename, mode) as f:
        f.write(var)

def _write(var, filename):
    _write_helper(var, filename, 'w')

def _append(var, filename):
    _write_helper(var, filename, 'a')

Binary = {
    'PIPE':   _pipe,
    '&>':     _write,
    '&>>':    _append,
    'ADD':    _add,
    'MUL':    _mul,
    'DIV':    _div,
    'MINUS':  _minus,
    'MOD':    _mod,
    'EQUAL':  _equal,
    'ASSINE': _assine,
    'AND':    _and,
    'OR':     _or,
}


Unary = {
    'OSCALL', None,
    'not': _not,
    'partial':None
}
