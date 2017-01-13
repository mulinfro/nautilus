from buildin_operators import operators, op_order, Binary, Unary

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        if (var in self): return self
        elif outer is None: return None
        else: return self.outer.find(var)

ast_stream = None

def parse(env):
    tp = ast_stream.peek()["type"]
    if tp == 'DEF': 
        parse_def(node, env)
    elif tp == 'IMPORT': 
        parse_import(node, env)
    else:
        parse_block_expr(node, env)

def gen_partial(f, env):
    return lambda node: f(node,env)
    
def parse_block_expr(node, env):
    if node["type"] == 'IF':
        val = parse_if(node, env)
    elif node["type"] == 'WHILE': 
        val = parse_while(node, env)
    elif node["type"] == "FOR":
        val = parse_for(node, env)
    else:
        val = parse_binary_expr(node, env)
    return val

def parse_assign(env):
    var = token.cur[1]
    token._next(2)
    val = parse_expr(node, env)
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

def parse_binary_expr(node, env):
    vals = map(gen_partial(parse_unary, env), node["val"])
    ops  = map(gen_partial(parse_op, env), node["op"])
    assert(len(vals) == len(ops) + 1)

    def compute_expr():
        def binary_order(left):
            if len(ops) > 0: my_op = ops.pop(0)
            else: return left

            # Logic short circuit
            if (my_op["name"] == 'OR' and left ) || (my_op["name"] == 'AND' and (not left)):
                return left

            right = vals.pop(0)()
            if len(ops) > 0:
                his_op = ops[0]
                if his_op["order"] > my_op["order"] or \
                    (his_op["order"] == my_op["order"] and not his_op["left"] ):
                    ops.pop(0)
                    right = binary_order(right)

            new_left = my_op["func"](left,right)
            return binary_order(new_left)

        left = vals.pop(0)(env)
        return binary_order(left)
    
    return compute_expr

# function call; var; literal value; unary operator
def parse_val_expr(node, env):
    op_func = None
    if token.get_cur_token_type() in Unary:
        op_func = parse_oper(token.get_cur_token_type())
    token._next()
    t_type = node["type"]
    if t_type is 'VAR':
        atom = parse_var(node, env)
    elif t_type is 'LIST': 
        atom = parse_list(node, env)
    elif t_type is 'TUPLE': 
        atom = parse_tuple(node, env)
    elif t_type is 'DICT': 
        atom = parse_dict(node, env)
    elif t_type is 'NUM':
        atom = lambda : node["val"]
    elif t_type is 'STRING':
        atom = parse_string(node, env)
    elif t_type is 'FUNC':
        atom = parse_func_call(node, env)
    elif t_type is 'PARTIAL':
        atom = parse_partial(node, env)
    elif t_type is 'LAMBDA':
        atom = parse_lambda(node, env)
    elif t_type is 'SIMPLE_IF':
        atom = parse_simple_if(node, env)
    if op_func:
        return lambda : op_func(atom())

def parse_list(node, env):
    l_vals = map(gen_parse(parse_expr, env), node["val"]))
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

def parse_func_call(node, env):
    pass

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
        t = env.find(var)
        if t is None: Error()
        return t[var]
    return find
    
def parse_block(node, env):
    pass

def parse_def(node, env):
    args = node["args"]
    default_vals = parse_expr(node["default_vals"], env)
    default_args = parse_expr(node["default_args"], env)
    new_env = Env(outer = env)
    def proc(args_vals, de_arg_vals):
        if len(args_vals) < len(args) or len(args_vals) > len(args) + len(default_args):
            Error("%s() unexpected argument number"% node["name"])
        for k,v in de_arg_vals:
            if k not in default_args:
                Error("%s() not defined argument %s"%(node["name"], k))
        new_env = Env(outer = env)
        # default args, every call re-eval, update them
        r_default_vals = [a(env) for a in default_vals]
        new_env.update(list(zip(default_args, r_default_vals))
        r_vals = [a(env) for a in args_vals]
        av = list(zip(args + default_args, r_vals))
        new_env.update(av)
        av = [ (k,v(env) ) for k,v in de_arg_vals ]
        new_env.update(av)

        try:
            body_f = parse_block(node["body"], new_env)
            return None
        except v:
            return v



