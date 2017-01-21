from buildin_operators import operators, op_order, Binary, Unary
import copy

class Return_exception(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Continue_exception(Exception):
    def __init__(self):
        self.value = "continue"
    def __str__(self):
        return repr(self.value)

class Break_exception(Exception):
    def __init__(self):
        self.value = "break"
    def __str__(self):
        return repr(self.value)

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
    if node["type"] == "ASSIGN":
        val = parse_assign(node, env)
    elif node["type"] == "PASSIGN":
        val = parse_pattern_assign(node, env)
    else:
        val = parse_simple_expr(node, env)
    return val

def parse_simple_expr(node, env):
    if node["type"] == "SIMPLEIF":
        val = parse_simpleif_expr(node, env)
    elif node["type"] == "BIEXPR":
        val = parse_binary_expr(node, env)
    elif node["type"] == "UNARY":
        val = parse_unary(node, env)
    else:
        val = parse_val_expr(node, env)
    return val

def parse_flow_goto(node, env):
    if node["type"] == "RETURN":
        rval = parse_expr(node["rval"], env)
        val = lambda: raise Return_exception(rval)
    elif node["type"] == "BREAK":
        val = Break_exception()
    else:
        val = Continue_exception()
    return lambda: raise val

def parse_import(node, env):
    file_path, package_name = package_path(node["packages"])
    if find_psh_file(file_path):
        package_env = pysh(file_path)
    else:
        import importlib
        i = importlib.import_module(file_path)

def parse_assign(node, env):
    val = parse_expr(node["val"], env)
    var = node["var"]["name"]
    return lambda :env[var] = val()

def parse_pattern_assign(node, env):
    val = parse_expr(node["val"], env)
    var = map(lambda x:x["name"], node["var"]["variables"])
    
    def _update():
        v = val()
        Run_assert(len(var) <= len(v), "error: to many variables")
        pairs = list(zip(var, v))
        tail = (pairs[-1][0], [pairs[-1][1]] + v[len(var)])
        pairs.pop()
        pairs.append(tail)
        for k, v in pairs:
            if k != "_":
                env[k] = v

        return _update
        
def parse_simpleif_expr(node, env):
    cond = parse_simple_expr(node["cond"], env)
    then = parse_simple_expr(node["then"], env)
    else_t = parse_simple_expr(node["else"], env)
    return lambda: then() if cond() else else_t()

def parse_return(node, env):
    val = parse_expr(node["rval"], env)
    return lambda: raise Return_exception(val)
    
def parse_bi_oper(node, env):
    op_info = {"name": node["val"], 
               "order": op_order(node["val"] ),
               "right": node["val"] in op_right,
               "func" : Binary[node["val"]] }
    return op_info

def parse_un_oper(node, env):
    return [Unary[v] for v in node["val"] ]

def parse_binary_expr(node, env):
    g_vals = map(gen_partial(parse_unary, env), node["val"])
    g_ops  = map(gen_partial(parse_bi_oper, env), node["op"])
    #assert(len(vals) == len(ops) + 1)

    def compute_expr():
        vals, ops = copy.copy(g_vals), copy.copy(g_ops)

        def binary_order(left):
            if len(ops) <= 0: return left
            my_op = ops.pop(0)

            # Logic short circuit
            if (my_op["name"] == 'OR' and left ) || (my_op["name"] == 'AND' and (not left)):
                return left

            right = vals.pop(0)()
            if len(ops) > 0:
                his_op = ops[0]
                if his_op["order"] > my_op["order"] or \
                    (his_op["order"] == my_op["order"] and his_op["right"]):
                    ops.pop(0)
                    right = binary_order(right)

            new_left = my_op["func"](left,right)
            return binary_order(new_left)

        left = vals.pop(0)()
        return binary_order(left)
    
    return compute_expr

def parse_args(node, env):
    syntax_cond_assert(node["type"] in ("ARGS", "TUPLE", "PARN", "PARTIAL"), "error type")
    arg_vals = map(gen_partial(parse_expr, env), node["val"])
    default_vals = []
    if node["type"] is "ARGS":
        default_vals = map(gen_partial(parse_expr, env), node["default_vals"])

    def _args():
        r_default_vals = map(lambda f: f(), default_vals)
        r_arg_vals = map(lambda f: f(), args_vals)
        zip(default_args, dft)
        return (r_arg_vals, dict(zip(r_default_args, r_default_vals)))

    return _args
    

def parse_suffix_op(node, env):
    for sn in node["val"]:
        if sn["type"] in ("PARN", "TUPLE", "ARGS"):
            snv = parse_args(sn, env)
            return lambda f: Unary["CALL"](f, snv())
        elif sn["type"] is "PARTIAL":
            return parse_partial(sn, env)
        elif sn["type"] is "DOT":
            return lambda x: x.__getattribute__(sn["attribute"])
        else:
            snv = parse_list(sn["val"], env)
            return lambda v: Unary["GET"](v, snv())

def parse_partial(node, env):
    h_args = parse_args(node, env)

    def _fdo(f):
        def _do(*p_args):
            total_args, i = [], 0
            for h in h_args:
                if h is not None:
                    total_args.append(h())
                else:
                    if i >= len(p_args): Runtime_error()
                    total_args.append(p_args[i])
                    i = i + 1
            if i < len(p_args): Runtime_error()
            return f(*p_args)
        return _do
    return _fdo


def parse_unary(node, env):
    prefix_ops = map(parse_un_oper, node["prefix"])
    prefix_ops.reverse()
    obj = parse_val_expr(node["obj"], env)
    suffix_ops = map(parse_suffix_op, node["suffix"])
    
    def _unary():
        v = obj()
        for sf in suffix_ops: v = sf(v)
        for pf in prefix_ops: v = pf(v)
        return v
    return _unary
        
# function call; var; literal value; unary operator
def parse_val_expr(node, env):
    t_type = node["type"]
    if t_type is 'VAR':
        atom = parse_var(node, env)
    elif t_type is 'LIST': 
        atom = parse_list(node, env)
    elif t_type is 'TUPLE':
        atom = parse_tuple(node, env)
    elif t_type is 'DICT': 
        atom = parse_dict(node, env)
    elif t_type in ("BOOL", 'NUM', 'STRING', "NONE"):
        atom = lambda : node["val"]
    elif t_type is 'SYSCALL':
        atom = parse_syscall(node, env)
    elif t_type is 'SYSFUNC':
        atom = parse_sysfunc(node, env)
    elif t_type is 'LAMBDA':
        atom = parse_lambda(node, env)
    else:
        Error()
    return atom

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
    cond = parse_simple_expr(node["cond"], env)
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

def parse_while(node, env):
    cond = parse_simple_expr(node["cond"], env)
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

def parse_sysfunc(node, env):
    def _do(args):
        commands = node["val"]% args
        return sys.popen(commands)
    return _do

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
    var = node["name"]
    def find():
        t = env.find(var)
        if t is None: Runtime_error()
        return t[var]
    return None if var == "_" else find
    
def squence_do(pf, exprs):
    exprs_lambda = map(pf, exprs)
    def _do():
        for expr in exprs_lambda: expr()

    return _do()

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
    pf = gen_partial(parse, env)
    body_f = squence_do(pf, node["body"])
    env[node["funcname"]] = proc

    def proc(*args_vals, **kwargs):
        if len(args_vals) < len(args) or len(args_vals) > len(args) + len(default_args):
            Error("%s() unexpected argument number"% node["name"])
        for k,v in kwargs.items():
            if k not in default_args:
                Error("%s() not defined argument %s"%(node["name"], k))
        new_env = Env(outer = env)
        # default args, every call re-eval, update them
        r_default_vals = [a(env) for a in default_vals]
        new_env.update(list(zip(default_args, r_default_vals))
        av = list(zip(args + default_args, arg_vals))
        new_env.update(av)
        new_env.update(kwargs)

        def _run():
            try:
                body_f(env)
                return None
            except Return_exception as r:
                return r.value

        return _run()
    return proc
