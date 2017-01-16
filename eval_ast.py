from buildin_operators import operators, op_order, Binary, Unary
import copy


class Return_exception(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repe(self.value)

class Continue_exception(Exception):
    def __init__(self):
        self.value = "continue"
    def __str__(self):
        return repe(self.value)

class Break_exception(Exception):
    def __init__(self):
        self.value = "break"
    def __str__(self):
        return repe(self.value)

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

def parse(node, env):
    tp = node["type"]
    if tp == 'DEF': 
        val = parse_def(node, env)
    elif tp == 'IMPORT': 
        val = parse_import(node, env)
    else:
        val = parse_block_expr(node, env)
    return val

def gen_partial(f, env):
    return lambda node: f(node,env)
    
def parse_block_expr(node, env):
    if node["type"] == 'IF':
        val = parse_if(node, env)
    elif node["type"] == 'WHILE': 
        val = parse_while(node, env)
    elif node["type"] == "FOR":
        val = parse_for(node, env)
    elif node["type"] in ["BREAK", "CONTINUE", "RETURN"]:
        val = parse_flow_goto(node, env)
    else:
        val = parse_expr(node, env)
    return val

def parse_expr(node, env):
    if node["type"] == "SIMPLEIF":
        val = parse_simpleif_expr(node, env)
    else:
        val = parse_binary_expr(node, env)
    return val

def parse_flow_goto(node, env):
    if node["type"] == "RETURN":
        return parse_return(node, env)
    elif node["type"] == "BREAK":
        val = Break_exception()
    else:
        val = Continue_exception()
    return lambda: raise val

def parse_import(env):
    pass

def parse_return(node, env):
    val = parse_expr(node["rval"], env)
    return lambda: raise Return_exception(val)
    
def parse_bi_oper(node, env):
    op_info = {"name": node["val"], 
               "order": op_order(node["val"] ),
               "right": node["val"] in op_right,
               "func" : Binary[node["val"]]
               }
    return op_info

def parse_un_oper(node, env):
    op_info = {"name": node["val"], 
               "func" : Unary[node["val"]] }
    return op_info

def parse_binary_expr(node, env):
    g_vals = map(gen_partial(parse_unary, env), node["vals"])
    g_ops  = map(gen_partial(parse_bi_oper, env), node["ops"])
    #assert(len(vals) == len(ops) + 1)

    def compute_expr():
        vals = copy.copy(g_vals)
        ops = copy.copy(g_ops)

        def binary_order(left):
            if len(ops) <= 0: return left
            my_op = ops.pop(0)

            # Logic short circuit
            if (my_op["name"] == 'OR' and left ) || (my_op["name"] == 'AND' and (not left)):
                return left

            right = vals.pop(0)
            if len(ops) > 0:
                his_op = ops[0]
                if his_op["order"] > my_op["order"] or \
                    (his_op["order"] == my_op["order"] and his_op["right"] ):
                    ops.pop(0)
                    right = binary_order(right)

            new_left = my_op["func"](left,right)
            return binary_order(new_left)

        left = vals.pop(0)(env)
        return binary_order(left)
    
    return compute_expr

def parse_unary(node, env):
    prefix_ops = map(parse_un_oper, node["prefix"])
    prefix_ops.reverse()
    obj = parse_val_expr(node["obj"], env)
    suffix_ops = node["suffix"]
    
    def _unary():
        v = obj()
        for sf in suffix_ops: v = sf(v)
        for pf in prefix_ops: v = pf(v)
        return v
    return _unary
        
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
    elif t_type is 'LAMBDA':
        atom = parse_lambda(node, env)
    if op_func:
        return lambda : op_func(atom())

def parse_list(node, env):
    l_vals = map(gen_parse(parse_expr, env), node["val"]))
    return lambda: map(lambda f: f(), l_vals) 

def parse_tuple(env):
    val = parse_list(node, env)
    return lambda: tuple(val())

def parse_dict():
    keys = parse_list(node["key"], env)
    vals = parse_list(node["val"], env)
    def _dict():
        t_key = map(lambda f: f(env), keys) 
        t_val = map(lambda f: f(env), vals) 
        return {}.update(list(zip(t_key, t_val)))
    return _dict
        
def return_none(env = {}):
    return None

def parse_if(node, env):
    cond = parse_expr(node["cond"], env)
    then_f = parse_block(node["then"], env)
    else_f = parse_block(node["else"], env)
    return lambda : then_f() if cond() else else_f()

def parse_for(node, env):
    in_f = parse_in(node["in"], env)
    body_f = parse_block(node["body"], env)

    def _for():
        iters = in_f()
        for g in iters:
            try:
                env.update(g)
                body_f()
            except Continue_exception:
                continue
            except Break_exception:
                break
        
    return _for

def parse_func_call(node, env):
    pass

def parse_while(node, env):
    cond = parse_expr(node["cond"], env)
    body_f = parse_block(node["body"], env)
    
    def _while():
        while cond():
            try:
                body_f()
            except Continue_exception:
                continue
            except Break_exception:
                break

    return _while

def parse_syscall(node, env):
    return lambda: sys.popen(node["val"])

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
    
def squence_do(pf, exprs):
    exprs_lambda = map(pf, exprs)
    def _do():
        for expr in exprs_lambda:
            expr()

def parse_block(node, env):
    exprs = map(gen_partial(parse, env), node)
    def squence_do():
        for expr in exprs: 
            expr()
        return ("SUCCESS", None)
    return squence_do

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
        new_env.update(de_arg_vals)
        pf = gen_partial(parse, env)
        body_f = squence_do(pf, node["body"])

        def _run():
            try:
                body_f(env)
                return None
            except Return_exception as r:
                return r.value

        return _run()
    env[node["funcname"]] = proc
    return proc
