from stream import stream
from char_stream import char_stream
from eval_ast import parse, Env
from ast_dict import AST
from tokens import token_list
from env import get_builtin_env

builtins = locals()["__builtins__"]
def REPL():

    IN = "$> "
    env = get_builtin_env(builtins)
    def is_block(cmd):
        return cmd.startswith("def ") or cmd.startswith("if ") \
            or cmd.startswith("for ") or cmd.startswith("while ")

    """
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
        #multiline_string_sep = check_multiline_string(cmd, multiline_string_sep)
    """

    cmdlines, block_num, = [], 0
    cmd = ""
    while True:
        cmd = cmd + input(IN).strip()
        # in repl every multiline need \
        if cmd.endswith("\\"):
            cmd = cmd[0:-1]
            continue

        cmdlines.append(cmd)
        if is_block(cmd): block_num = block_num + 1
        if cmd.endswith("end"): 
            if len(cmd) == 3 or cmd[-4] in [" ", "\t"]:
                block_num = block_num - 1
        cmd = ""
            
        if block_num == 0:
            fragment = char_stream("\n".join(cmdlines) +"\n")
            cmdlines = []
            tokens = token_list(fragment).tokens
            print("tokens", tokens)
            ast_tree = AST(stream(tokens))
            for node in ast_tree.ast:
                ans = parse(node)(env)
                if isinstance(ans, types.GeneratorType):
                    for e in ans: print(":> ", e)
                else:
                    print(":> ", ans)
            

def pysh(psh_file):
    with open(psh_file) as f:
        codes = char_stream(f.read())
    env = get_builtin_env(builtins)
    tokens = token_list(codes).tokens
    ast_tree = AST(stream(tokens))
    for node in ast_tree.ast:
        try:
            print(parse(node)(env))
        except:
            print(node)
            print(parse(node)(env))

    if "main" in env:
        import sys
        main(*sys.argv[1:])
        


if __name__ == "__main__":
    pysh("test2.psh")
    REPL()
