from stream import stream
from char_stream import char_stream
from eval_ast import parse, Env
from ast_dict import AST
from tokens import token_list

builtins = locals()["__builtins__"]

def get_builtin_env():
    paras = dir(builtins)
    args  = [builtins.__dict__.get(a) for a in paras]
    return Env(parms = paras, args =args)

def REPL():

    IN = "$> "
    env = get_builtin_env()
    def is_block(cmd):
        return cmd.startswith("def ") or cmd.startswith("if ") \
            or cmd.startswith("for ") or cmd.startswith("while ")

    def check_multiline_string(cmd, multiline_string_sep):
        line_str = False
        for i in range(0, len(cmd)-2):
            if line_str:
                if line_str == cmd[i]: line_str = False
            elif cmd[i] in ("'", '"'):
                if cmd[i+1] == cmd[i] and cmd[i+2] == cmd[i]:
                    if multiline_string_sep is None:
                        return check_multiline_string(cmd[i+3:], cmd[i])
                    elif cmd[i] == multiline_string_sep:
                        return check_multiline_string(cmd[i+3:], None)
                elif multiline_string_sep is None:
                    line_str = cmd[i]
        return multiline_string_sep

    cmdlines, block_num, multiline_string_sep  = [], 0, None
    cmd = ""
    while True:
        cmd = cmd + input(IN).strip()
        if cmd.endswith("\\"):
            cmd = cmd[0:-1]
            continue

        cmdlines.append(cmd)
        if not multiline_string_sep and is_block(cmd): block_num = block_num + 1
        multiline_string_sep = check_multiline_string(cmd, multiline_string_sep)
        if not multiline_string_sep and cmd.endswith(" end"): block_num = block_num - 1
        cmd = ""
            
        if not multiline_string_sep and block_num == 0:
            fragment = char_stream("\n".join(cmdlines) +"\n")
            print("CMDLINES", cmdlines)
            cmdlines = []
            tokens = token_list(fragment).tokens
            ast_tree = AST(stream(tokens))
            for node in ast_tree.ast:
                fval = parse(node, env)
                print(":> ", fval())
            

def pysh(psh_file):
    with open(psh_file) as f:
        codes = char_stream(f.read())
    tokens = token_list(codes).tokens
    ast_tree = AST(stream(tokens))
    for node in ast_tree.ast:
        parse(node, env)()

    if "main" in env:
        import sys
        main(*sys.argv[1:])
        


if __name__ == "__main__":
    REPL()
