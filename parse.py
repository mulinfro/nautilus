
op_order = {
        "=": 1,
        "||": 2,
        "&&": 3,
        "|": 5,
        "<": 7, ">": 7, "<=": 7, ">=": 7, "==": 7, "!=": 7,
        "+": 10, "-": 10,
        "*": 20, "/": 20, "%": 20,
        }

class tokens():

    def __init__():
        pass


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)


def parse(env):
    if token.cur[0] == 'VAR':
        if token.next[0].type == 'ASSIGN':
            parse_assign(env)
        else if token.next[0].type in ('ATOM', 'VAR'): 
            parse_funcall(env)
        else if token.next[0].type == 'OP': 
            parse_expr(env)
        else if token.next[0].type in ('IF','FOR', 'FOREACH', 'WHILE'): 
            parse_control(env)
        else if token.next[0].type == 'DEF': 
            parse_def(env)
        else if token.next[0].type == 'LAMBDA': 
            parse_lambda(env)
        else if token.next[0].type == 'IMPORT': 
            parse_import(env)

def parse_control(env):
    if token.next[0].type == 'IF':
        parse_if(env)

def parse_assign(env):
    var = token.cur[1]
    token._next(2)
    val = parse_expr(env)
    def assign(env):
        env[var ] = val()
    return assign

def parse_import(env):
    pass

def parse_oper(oper_type):
    if oper_type in Unary:
        return Unary[oper_type]
    else if oper_type in Binary:
        return Binary[oper_type]
    Error()
    return None

def parse_expr(env):
    op_stack = []
    val_stack = []
    val_stack.append(parse_simple_expr(env))
    while token.get_cur_token_type() in Binary:
        op_stack.append( (op_order[token.get_cur_token_type()], parse_oper(token.get_cur_token_type()) ))
        token._next()
        val_stack.append(parse_simple_expr(env))

    def compute_expr():
        def binary_order(left):
            if len(op_stack()) > 0: my_op = op_stack.pop(0)
            else: return left

            # Logic short circuit
            if (my_op[0] == op_order['OR'] and left ) || (my_op[0] == op_order['AND'] and (not left)):
                return left

            his_op = op_stack[0]
            right = val_stack.pop(0)()
            if his_op[0] > my_op[0]:
                op_stack.pop(0)
                right = binary_order(right, his_op)

            new_left = my_op[1](left,right)
            return binary_order(new_left)

        left = val_stack.pop(0)()
        return binary_order(left)
    
    return compute_expr


# function call; var; literal value; unary operator
def parse_simple_expr(env):
    op_func = None
    if token.get_cur_token_type() in Unary:
        op_func = parse_oper(token.get_cur_token_type())
    token._next()
    t_type = token.get_cur_token_type()
    if t_type is 'VAR':
        atom = parse_var(env)
    else if t_type is 'LIST': 
        atom = parse_list(env)
    else if t_type is 'TUPLE': 
        atom = parse_tuple(env)
    else if t_type is 'DICT': 
        atom = parse_dict(env)
    else if t_type in ('STRING','NUM'):
        val = token.get_cur_token_value()
        atom = lambda : val
    if op_func:
        return lambda : op_func(atom())

def parse_list(env):
    pass

def parse_tuple(env):
    val = parse_list(env)
    return lambda: tuple(val())

def parse_dict():
    pass

def return_none(env = {}):
    return None

def parse_if(env):
    token._next()
    if token.cur[0] != 'PARN': Error()
    cond_lambda,env_cond = parse_expr(env)
    then_lambda,env_then = parse_block(env):
    if token.cur[0] != 'ELSE':
        else_lambda, env_else = parse_block(env)
    return (lambda : then_lambda(env_then) if (cond_lambda(env)) else else_lambda(env_else) , env)

def parse_for(env):
    
def parse_lambda(env):
    token._next()
    arg_var_list = parse_args(env)
    def proc(arg_val_list):
        inner_env = Env(env)
        inner_env.update(zip(arg_var_list, arg_val_list))
        return parse_expr(inner_env)
    return proc

def parse_atom(env):
    val = token.cur[1]
    token._next()
    return val

def parse_var(env):
    var = token.cur[1]
    def find():
        if var not in env:
            Error()
        return env.find(var)[var]
    return find
    
def parse_block(env):
    pass

def parse_def(env):
    pass
