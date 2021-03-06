"""
    builtin operators
"""
import operator

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
    '=': 'ASSIGN',
    ':': 'COLON',
    "<": "LT",
    ">": "GT",
    "<=": "LE",
    ">=": "GE",
    '==':'EQUAL',
    "!=": "NEQ",
    ".": "DOT",
    "is":"IS",
    "in":"IN",
}

special_op = {
    '::': 'PASSIGN',
    '=': 'ASSIGN',
    ':=': 'GASSIGN',
}

op_order = {
    'WRITE':1,
    'APPEND':1,
    "OR": 3,
    "AND": 4,
    "IS": 5, "IN": 5,
    "PIPE": 6,
    "LT": 7, "GT": 7, "LE": 7, "GE": 7, "EQUAL": 7, "NEQ": 7,
    "ADD": 10, "MINUS": 10,
    "MUL": 20, "DIV": 20, "MOD": 20,
}

# 结合性; 右结合
op_right = {
    "EQUAL": 2,
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
_pipe = lambda x,f: f(x)
_in  = lambda x,y: x in y
_is  = lambda x,y: x is y

"""
def _pipe(x,f):
    import types
    if not isinstance(x, types.GeneratorType):
        yield f(x)
    else:
        for sx in x:
            yield f(sx)
"""

def _write_helper(var, filename, mode):
    import types
    with open(filename, mode) as f:
        if isinstance(var, types.GeneratorType):
            for e in var: f.write(str(var) + "\n")
        else:
            f.write(str(var))
        

def _write(var, filename):
    _write_helper(var, filename, 'w')

def _append(var, filename):
    _write_helper(var, filename, 'a')

def _call(f, arg):
    return f(*arg[0], **arg[1])

def _get_dict(v, k):
    r = [v[ki] if ki in v else None for ki in k]
    if len(r) == 1: return r[0]
    return r

def _get(v, k):
    if type(v) is dict: return _get_dict(v,k)
    if len(k) == 1: return v[k[0]]
    else: return [v[ki] for ki in k]

def _assign(var, val, env):
    env[var] = val
    return val

def _return(v):
    raise v

Binary = {
    'PIPE':   _pipe,
    'WRITE':  _write,
    'APPEND': _append,
    'ADD':    _add,
    'MUL':    _mul,
    'DIV':    _div,
    'MINUS':  _minus,
    'MOD':    _mod,
    'EQUAL':  _equal,
    'ASSIGN': _assign,
    'AND':    _and,
    'OR':     _or,
    "IS":     _is,
    "IN":     _in,
    "GT":     operator.gt,
    "GE":     operator.ge,
    "LT":     operator.lt,
    "LE":     operator.le,
    "NEQ":    operator.ne,
    "EQUAL":  operator.eq,
}


Unary = {
    'OSCALL': None,
    'ADD': lambda x:x,
    'MINUS': lambda x:-x,
    'NOT': _not,
    "CALL": _call,
    "GET" : _get,
    "RETURN": _return,
}
