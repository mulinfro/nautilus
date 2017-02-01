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

def pysh(psh_file = "test2.psh"):
    env = get_builtin_env()
    with open(psh_file) as f:
        codes = char_stream(f.read())
    #print(codes._stream)
    print("\n")
    tokens = token_list(codes).tokens
    #stream(tokens)
    ast_tree = AST(stream(tokens))
    for node in ast_tree.ast:
        print(":> ", parse(node, env)())
    """
    print("++++++++++++++++++++++++++++++++++", "www")
    for a in ast_tree.ast:
        print(a)
    for token in tokens:
        #print (token)
        print(token)

    ast_tree = AST(tokens.tokens)
    for node in ast_tree.ast:
        parse(node, env)()
        """


if __name__ == "__main__":
    pysh()
