from builtin import operators, op_order, Binary, Unary, op_right
import copy,sys
from syntax_check import Error, syntax_cond_assert

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
        self.globals = outer.globals if outer else self
    def find(self, var):
        "Find the innermost Env where var appears."
        if (var in self): return self
        elif self.outer is None: return None
        else: return self.outer.find(var)

def parse(node):
    if  node["type"] == 'DEF': 
        val = parse_def(node)
    elif node["type"] == 'IMPORT': 
        val = parse_import(node)
    else:
        val = parse_block_expr(node)
    return val

def parse_block_expr(node):
    if node["type"] == 'IF':
        val = parse_if(node)
    elif node["type"] == 'WHILE': 
        val = parse_while(node)
    elif node["type"] == "FOR":
        val = parse_for(node)
    elif node["type"] in ["BREAK", "CONTINUE", "RETURN"]:
        val = parse_flow_goto(node)
    else:
        val = parse_expr(node)
    return val

def parse_expr(node):
    if node["type"] in ("ASSIGN", "GASSIGN"):
        val = parse_assign(node)
    elif node["type"] == "PASSIGN":
        val = parse_pattern_assign(node)
    else:
        val = parse_simple_expr(node)
    return val

def parse_simple_expr(node):
    if node["type"] == "SIMPLEIF":
        val = parse_simpleif_expr(node)
    elif node["type"] == "BIEXPR":
        val = parse_binary_expr(node)
    else:
        val = parse_unary(node)
    return val

def parse_flow_goto(node):
    if node["type"] == "RETURN":
        rval = parse_expr(node["rval"])
        val = Return_exception(rval)
    elif node["type"] == "BREAK":
        val = Break_exception()
    else:
        val = Continue_exception()

    def _raise_error(val):
        raise val
    return lambda: _raise_error(val)

def parse_import(node):

    import sys, os, importlib
    def get_module_path(_from, p_num):
        path = "/".join(_from)
        parents = "../" * p_num
        t = sys.argv[0] + "/" + parents + path
        path = os.path.realpath(t)
        return path

    def find_psh_file(path):
        if os.path.isfile( path  + ".py"):
            return (True, False, ".py")
        elif os.path.isfile(path + ".psh"):
            return (True, False, ".psh")
        elif os.path.exists(path):
            return (False, True, False)
        else:
            return (False, False, False)

    def python_import(_from, _import, _as):
        if _from: 
            top_module = __import__( ".".join(_from) )
            for t in _from[1:]:
                top_module = top_module.__getattribute__(t)
                env[_as] = top_module.__getattribute__(_import[0])
        else:
            env[_as] = __import__(_import[0])
            
    def user_import_py(path, _as):
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(_as, path).load_module()

    def user_package_import():
        pass

    def user_import_package(path):
        pass
    def user_import_psh(path):
        pass
    def user_package_import(path, file_suffix):
        if file_suffix == ".py":
            return user_import_py(path + file_suffix, _as)
        elif file_suffix == ".psh":
            return user_import_psh(path)
        else:
            onlyfiles = [ f for f in os.listdir(path) ]
            env[_as] = user_import_package(path)

    _from, _import, _as = node["from"], node["import"], node["as"]
    if len(_as) == 0:
        if _from: _as = [ m[-1] for m in _import ]
        else: _as = [ m[0] for m in _import ]
    module_path = get_module_path(_from, node["p_num"] )
    isfile, isdir, file_suffix = find_psh_file(module_path)
    for i in range(len(_import)):
        if isfile or isdir:
            package_env = user_package_import(module_path, file_suffix, _import[i], _as[i])
        else:
            python_import(_from, _import[i], _as[i])

def parse_assign(node):
    val = parse_expr(node["val"])
    var = node["var"]["name"]
    def _assign(v, env):
        if node["type"] == "GASSIGN": env = env.globals
        env[var] = v
        return v
    return lambda env: _assign(val(), env)

def lst_combine(var, v):
    syntax_cond_assert(len(var) <= len(v), "error: to many variables")
    pairs = list(zip(var, v))
    tail = (pairs[-1][0], [pairs[-1][1]] + v[len(var)])
    pairs.pop()
    pairs.append(tail)
    return pairs

def parse_pattern_assign(node):
    val = parse_expr(node["val"])
    var = node["var"]["variables"]
    
    def _update():
        if node["type"] == "GASSIGN": env = env.globals
        env.update(lst_combine(var, val()))
    return _update
        
def parse_simpleif_expr(node):
    cond = parse_simple_expr(node["cond"])
    then = parse_simple_expr(node["then"])
    else_t = parse_simple_expr(node["else"])
    return lambda env: then(env) if cond(env) else else_t(env)

def parse_bi_oper(node):
    op_info = {"name": node["val"], 
               "order": op_order[node["val"] ],
               "right": node["val"] in op_right,
               "func" : Binary[node["val"]] }
    return op_info


def parse_binary_expr(node):
    g_vals = list(map(parse_unary, node["val"]))
    g_ops  = list(map(parse_bi_oper, node["op"]))
    '''
    print("binary", node["val"], node["op"])
    print("binary", g_vals, g_ops)
    for g in g_vals:
        print("ggg", g())
        '''

    def compute_expr(env):
        vals, ops = copy.copy(g_vals), copy.copy(g_ops)

        def binary_order(left):
            if len(ops) <= 0: return left
            my_op = ops.pop(0)

            # Logic short circuit
            if (my_op["name"] == 'OR' and left ) or (my_op["name"] == 'AND' and (not left)):
                return left

            right = vals.pop(0)(env)
            if len(ops) > 0:
                his_op = ops[0]
                if his_op["order"] > my_op["order"] or \
                    (his_op["order"] == my_op["order"] and his_op["right"]):
                    ops.pop(0)
                    right = binary_order(right)

            new_left = my_op["func"](left,right)
            return binary_order(new_left)

        left = vals.pop(0)(env)
        return binary_order(left)
    
    return compute_expr

def parse_args(node):
    syntax_cond_assert(node["type"] in ("ARGS", "TUPLE", "PARN", "PARTIAL"), "error type")
    arg_vals = list(map(parse_expr, node["val"]))
    default_vals = []
    if node["type"] is "ARGS":
        default_vals = list(map(parse_expr, node["default_vals"]))

    def _args(env):
        r_default = {}
        if "default_args" in node:
            r_default_vals = [f(env) for f in default_vals]
            r_default = dict(zip(node["default_args"], r_default_vals))
        r_arg_vals = [f(env) for f in arg_vals]
        return (r_arg_vals, r_default)

    return _args
    

def parse_suffix_op(op):
    if op["type"] in ("PARN", "TUPLE", "ARGS"):
        snv = parse_args(op)
        return lambda f: Unary["CALL"](f, snv())
    elif op["type"] is "PARTIAL":
        return parse_partial(op)
    elif op["type"] is "DOT":
        return lambda x: x.__getattribute__(op["attribute"])
    else:
        snv = parse_list(op["val"])
        return lambda v,env: Unary["GET"](v, snv(env))

def parse_partial(node):
    h_args = parse_args(node)

    def _fdo(f):
        def _do(*p_args):
            total_args, i = [], 0
            for h in h_args:
                if h is not None:
                    total_args.append(h())
                else:
                    if i >= len(p_args): Error()
                    total_args.append(p_args[i])
                    i = i + 1
            if i < len(p_args): Error()
            return f(*p_args)
        return _do
    return _fdo


def parse_unary(node, env):
    if node["type"] != "UNARY": return parse_val_expr(node, env)
    prefix_ops = [Unary[v] for v in node["prefix"] ]
    prefix_ops.reverse()
    obj = parse_val_expr(node["obj"], env)
    suffix_ops = list(map(gen_partial(parse_suffix_op, env), node["suffix"]))
    
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
        #print("val_expr: " + t_type)
        Error("val_expr: " + t_type)
    return atom

def parse_list_comp(node, env):
    interval = lambda: 1
    if 1 != node["interval"]:
        interval = parse_expr(node["interval"], env)
    beg = parse_expr(node["beg"], env)
    end = parse_expr(node["end"], env)

    def _list_range():
        beg_v = beg()
        end_v = end()
        interval_v = interval()
        return range(beg_v, end_v, interval_v)

    return  _list_range

def parse_list(node, env):
    expr_partial = gen_partial(parse_expr, env)
    res = []
    for ele in node["val"]:
        if ele["type"] == "LISTCOM":
            res.append(("COMP", parse_list_comp(ele, env)))
        else:
            res.append(("ELE", expr_partial(ele)))

    def _p_list():
        v = []
        for r in res:
            if r[0] == "COMP": v.extend(r[1]())
            else:  v.append(r[1]())
        return v

    return _p_list

def parse_tuple(node, env):
    val = parse_list(node, env)
    return lambda: tuple(val())

def parse_dict(node, env):
    keys = parse_list(node["key"], env)
    vals = parse_list(node["val"], env)
    def _dict():
        t_key = list(map(lambda f: f(env), keys))
        t_val = list(map(lambda f: f(env), vals))
        return {}.update(list(zip(t_key, t_val)))
    return _dict
        
def return_none(env = {}):
    return None

def parse_if(node, env):
    cond = parse_simple_expr(node["cond"], env)
    then_f = parse_block(node["then"], env)
    else_f = parse_block(node["else"], env)
    return lambda : then_f() if cond() else else_f()

def parse_in(node, env):
    v = parse_expr(node["val"], env)
    def _in():
        var = node["var"]["name"]
        for ele in v():
            yield [(var, ele)]

    def _p_in():
        var = node["var"]["variables"]
        for ele in v():
            yield lst_combine(var, ele)

    return _p_in if node["var"]["type"] == "PATTERNVAR" else _in

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

def os_call(sh):
    #print("SH:", sh)
    import subprocess
    out_bytes = subprocess.check_output(sh)
    return out_bytes.decode('utf-8')

def parse_syscall(node, env):
    return lambda :os_call(node["val"])

def parse_sysfunc(node, env):
    return lambda args: os_call(node["val"]% args)

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
        if t is None: Error()
        return t[var]
    return None if var == "_" else find
    
def squence_do(pf, exprs):
    exprs_lambda = list(map(pf, exprs))
    def _do():
        for expr in exprs_lambda: expr()

    return _do()

def parse_block(node, env):
    exprs = list(map(gen_partial(parse, env), node))
    def squence_do():
        for expr in exprs: 
            expr()
        return ("SUCCESS", None)
    return squence_do

def parse_def(node, env):
    args = node["args"]
    print("NODE", node)
    print("ARGS", args)
    default_args, default_vals = [], []
    if "default_args" in args:
        default_vals = parse_expr(args["default_vals"], env)
        default_args = parse_expr(args["default_args"], env)

    pf = gen_partial(parse, env)
    body_f = squence_do(pf, node["body"])

    def proc(*args_vals, **kwargs):
        if len(args_vals) < len(args) or len(args_vals) > len(args) + len(default_args):
            Error("%s() unexpected argument number"% node["name"])
        for k,v in kwargs.items():
            if k not in default_args:
                Error("%s() not defined argument %s"%(node["name"], k))
        new_env = Env(outer = env)
        # default args, every call re-eval, update them
        r_default_vals = [a(env) for a in default_vals]
        new_env.update(list(zip(default_args, r_default_vals)))
        av = list(zip(args + default_args, args_vals))
        new_env.update(av)
        new_env.update(kwargs)

        def _run():
            try:
                body_f(new_env)
                return None
            except Return_exception as r:
                return r.value

        return _run

    env[node["funcname"]] = proc
    return lambda: "function: " + node["funcname"]
