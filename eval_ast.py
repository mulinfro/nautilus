from buildin_operators import operators, op_order, Binary, Unary

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)

ast_stream = None

def parse(env):
    tp = ast_stream.peek()["type"]
    if tp == 'DEF': 
        parse_def(node, env)
    elif tp == 'IMPORT': 
        parse_import(node, env)
    else:
        parse_block_expr(node, env)

def parse_partial(f, env):
    return lambda node: f(node,env)
    
def parse_control(node, env):
    if node["type"] == 'IF':
        parse_if(node, env)
    elif node["type"] == 'WHILE': 
        parse_while(node, env)
    elif node["type"] == "FOR":
        parse_for(node, env)

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

def parse_binary_expr(env):
    op_stack = []
    val_stack = []
    val_stack.append(parse_val_expr(env))
    while token.get_cur_token_type() in Binary:
        op_stack.append( (op_order[token.get_cur_token_type()], parse_oper(token.get_cur_token_type()) ))
        token._next()
        val_stack.append(parse_val_expr(env))

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
def parse_val_expr(env):
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
    else if t_type is 'NUM':
        val = token.get_cur_token_value()
        atom = lambda : val
    else if t_type is 'STRING':
        atom = parse_string(env)
    else if t_type is 'FUNC':
        atom = parse_func_call(env)
    else if t_type is 'PARTIAL':
        atom = parse_partial(env)
    else if t_type is 'LAMBDA':
        atom = parse_lambda(env)
    else if t_type is 'SIMPLE_IF':
        atom = parse_simple_if(env)
    if op_func:
        return lambda : op_func(atom())

def parse_list(node, env):
    l_vals = map(parse_partial(parse_expr, env), node["val"]))
    return lambda: map(lambda f: f(env), l_vals) 

def parse_tuple(env):
    val = parse_list(node, env)
    return lambda: tuple(val())

def parse_dict():
    keys = parse_list(node["key"], env)
    vals = parse_list(node["val"], env)
    def _dict():
        t_key = map(lambda f: f(env), keys) 
        t_val = map(lambda f: f(env), vals) 
        return {}.update(zip(t_key, t_val)
    return _dict
        
def return_none(env = {}):
    return None

def parse_if(node, env):
    cond = parse_expr(node["cond"], env)
    then_f = parse_block(node["then"], env)
    else_f = parse_block(node["else"], env)
    return lambda : then_f(env) if cond(env) else else_f(env)

def parse_for(node, env):
    in_f = parse_in(node["in"], env)
    cond = parse_expr(node["cond"], env)
    body_f = parse_block(node["body"], env)

    def _for():
        g = in_f(env)
        while True:
            try:
                env.update(next(g))
                if cond(env): body_f(env)
            except StopIteration:
                break
        
    return _for

def parse_func_call():

def parse_while(node, env):
    cond = parse_expr(node["cond"], env)
    body_f = parse_block(node["body"], env)
    
    def _while():
        while cond(env):
            body_f(env)

    return _while

# Q default args
def parse_lambda(node, env):
    arg_var_list = parse_args(node["args"], env)
    new_env = Env(outer = env)
    body_f = parse_expr(node["body"], new_env)
    def proc(*arg_val_list):
        new_env.update(zip(arg_var_list,arg_val_list))
        return body_f(new_env)
    return proc

def parse_atom(node, env):
    return lambda: node["val"]

def parse_var(node, env):
    var = node["var"]
    def find():
        if var not in env:
            Error()
        return env.find(var)[var]
    return find
    
def parse_block(env):
    pass

def parse_def(env):
    pass
