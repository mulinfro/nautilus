from char_stream import char_stream
from eval_ast import parse

def get_builtin_env():
    builtins = locals()["__builtins__"]
    paras = dir(builtins)
    args  = [builtins.__dict__.get(a) for a in paras]
    return eval_ast.Env(parms = paras, args =args)

def REPL():

    IN = "$> "
    env = get_builtin_env()
    def is_block(cmd):
        return cmd.startswith("def ") or cmd.startswith("if ") \
            or cmd.startswith("for ") or cmd.startswith("while ")

    def check_multiline_string(cmd, multiline_string_sep):
        for i in range(0, len(cmd)-2):
            if cmd[i] in (",", '"') and cmd[i+1] == cmd[i] and cmd[i+2] == cmd[i]:
                if multiline_string_sep is None:
                    return check_multiline_string(cmd[i+3:], cmd[i])
                elif cmd[i] == multiline_string_sep:
                    return check_multiline_string(cmd[i+3:], None)
        return multiline_string_sep

    cmdlines, block_num, multiline_string_sep  = [], 0, None
    while True:
        cmd = cmd + input(IN).strip()
        if cmd.endswith("\\"):
            cmd = [0:-1]
            continue

        cmdlines.append(cmd)
        if not multiline_string_sep and is_block(cmd): block_num = block_num + 1
        multiline_string_sep = check_multiline_string(multiline_string_sep)
        if not multiline_string_sep and cmd.endswith(" end"): block_num = block_num - 1
        cmd = ""
            
        if not multiline_string_sep and block_num == 0:
            fragment = char_stream("\n".join(cmdlines) )
            ast_tree = AST(fragment)
            fval = parse(ast_tree.ast, env)
            print(fval())
            

def pysh(psh_file):
    with open(psh_file) as f:
        codes = char_stream(f.read())
    ast_tree = AST(codes)
    for node in ast_tree.ast:
        parse(node, env)()

    if "main" in env:
        import sys
        main(*sys.argv[1:])
        

