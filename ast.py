from stream import stream
import sys

'''
    def ast_not_if_expr(self, stm):
        tkn = stm.peek()
        if tkn.tp is "PARN":
            stm.next()
            return self.ast_parn_expr(tkn.val, self.check_eof)
        else:
            return self.ast_binary_expr(stm)
'''

class AST():
    
    def __init__(self, tokens):
        self.tokens = stream(tokens)
        self.ast = []
        build_ast()

    def build_ast(self):
        while not self.tokens.eof():
            self.newlines()
            tkn = self.tokens.peek()
            if tkn.tp is 'DEF':
                self.ast.append(self.ast_def(self.tokens))
            elif tkn.tp in 'IMPORT':
                self.ast.append(self.ast_import(self.tokens))
            else:
                self.ast.append(self.ast_block_expr(self.tokens))

    def ast_import(self, stm):
        
        return ("IMPORT", packages)

    def ast_same_type_seq(self, stm, is_valid):
        tps = []
        while not stm.eof() and is_valid(stm.peek()):
            tps.append(stm.next().val)
        return tps

    def newlines(self, stm):
        is_valid = lambda tkn: tkn.tp == "NEWLINE"
        vals = self.ast_same_type_seq(stm, is_valid)
        return len(vals) > 0

    def ast_block_expr(self, stm):
        if stm.peek().tp in ['IF', 'FOR', 'WHILE']:
            return self.ast_control(stm)
        else:
            return self.ast_expr(stm)

    def ast_control(self, stm):
        tkn = stm.peek()
        if   tkn.tp is 'IF':
            return self.ast_if(stm)
        elif tkn.tp is 'FOR':
            return self.ast_for(stm)
        elif tkn.tp is 'WHILE':
            return self.ast_while(stm)

    def ast_parn(self, stm):
        vals = []
        is_tuple = False
        while not stm.eof():
            vals.append(self.parse_expr(stm))
            if not stm.eof():
                is_tuple = True
                syntax_assert(("SEP","COMMA"), stm.next(), "missing comma ,")
        tp = "PARN"
        if is_tuple or len(vals) == 0:
            tp = "TUPLE"
        return {"type":tp, "val":vals}
                
    def check_expr_end(self, stm):
        if not stm.eof():
            self.check_newline(stm)

    def check_newline(self, stm):
        syntax_assert(stm.next().tp, "NEWLINE", False, "syntax error")

    def check_eof(self, stm):
        syntax_assert(stm.eof(), True, False, "syntax error")

    def ast_expr(self, stm, end_checker=lambda: True):
        true_part, cond, else_part = [], [], []
        true_part = self.ast_binary_expr(stm)
        if not stm.eof() and stm.peek().tp is "IF":
            stm.next()
            cond = self.ast_binary_expr(stm)
            syntax_assert(stm.next().tp, "ELSE", False, "syntax error")
            else_part = self.ast_binary_expr(stm)
            end_checker(stm)
            return {"type":"SIMPLEIF", "then":true_part,
                    "cond":cond, "else":else_part}

        end_checker(stm)
        return true_part
                
    def ast_def(self, stm):
        stm.next()
        funcname = self.ast_a_var(stm, "need funcname")
        if stm.peek().tp not in ("PARN", "TUPLE"): Error("")
        args = ast_args(stream(stm.next().val))
        body = self.ast_body(self.ast_func_body)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":'DEF', "funcname":funcname, 
                "args":args, "body":body}
        
    def ast_args(self, stm, is_end_tkn):
        args, default_args, default_vals = [], [], []
        need_default = False
        while not stm.eof():
            arg = self.ast_a_var(stm)
            if need_default or \
                (not stm.eof() and syntax_check(stm.looknext(),("SEP","COMMA"), _not=True)):
                syntax_assert(stm.next(), ("OP","ASSIGN"), \
                      "non-default argument follows default argument")
                default_value = self.ast_expr(stm)
                default_args.append(arg)
                default_vals.append(default_value)
                need_default = True

            if not stm.eof():
                syntax_assert(stm.next(), ("SEP","COMMA"), "missing comma")
        return {"type":"ARGS", "args":args, 
                "default_args":default_args, 
                "default_vals":default_vals}

    def ast_body(self, stm, parse_func = self.ast_func_body):
        body = []
        while True:
            self.newlines(stm)
            if stm.peek().tp in ("ELSE", "END"): return body
            body.append(parse_func(stm))
    
    def ast_func_body(self, stm):
        tkn = stm.peek()
        if tkn.tp is 'DEF':
            return self.ast_def(stm)
        else:
            return self.ast_block_expr(stm)
        
    def ast_a_var(self, stm, error_msg = "expect a variable"):
        tkn = stm.next()
        syntax_assert(tkn.tp,"VAR", error_msg)
        return tkn.val

    def ast_if(self, stm):
        stm.next(); tkn = stm.next()
        syntax_assert(tkn, "PARN", "need parn")
        cond = self.ast_expr(stream(tkn.val), self.check_eof)
        true_part = self.ast_body(stm, self.ast_block_expr)
        tkn, else_part = stm.peek(), None
        if tkn.tp is "ELSE":
            else_part = self.ast_body(stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":'IF', "cond":cond, "then":true_part, "else":else_part)
        
    def ast_for(self, stm):
        stm.next(); tkn = stm.next()
        syntax_assert(tkn, "PARN",  "missing (")
        _in = self.ast_in(stream(tkn.val))
        body = self.ast_body(self, stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":"FOR", "in":_in, "body":body}

    def ast_while(self, stm):
        stm.next(); tkn = stm.next()
        syntax_assert(tkn.tp, "PARN",  "missing (")
        cond = self.ast_expr(stream(tkn.val))
        body = self.ast_body(self, stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":"WHILE", "cond":cond, "body":body}

    def ast_pattern_var(self, stm):
        variables = [self.ast_a_var(stm)]
        while syntax_check(stm.peek(), ("OP","PATTERN")):
            stm.next()
            variables.append(self.ast_a_var(stm))

        if len(variables) > 1: 
            return ("PATTERNVAR", variables)
        else:
            return ("VAR", variables[0])

    def ast_in(self, stm):
        var = self.ast_pattern_var(stm)
        syntax_assert(stm.next(), "IN", "error syntax in for setence", True)
        val = self.ast_expr(stm)
        return {"type":"IN", "ISPATTERN":var[0], "var":var[1], "val":val }

    def ast_unary(self, stm):
        prefix = self.ast_prefix_op(stm)
        obj_val = self.ast_val(stm)
        suffix = self.ast_suffix_op(stm)
        return {"type":"UNARY", "prefix":prefix,
                "obj":obj_val, "suffix":suffix}

    def ast_prefix_op(self, stm):
        is_valid = lambda tkn: tkn.tp is "OP" and tkn.val in Unary
        tps = self.ast_same_type_seq(stm, is_valid)
        return {"type":"PREFIXOP", "val":tps}

    def ast_suffix_op(self, stm):
        tps = []
        while not stm.eof() and stm.peek().tp in ("LIST", "PARN", "TUPLE" ):
            tps.append(ast_val(stm))

        return {"type":"SUFFIXOP", "val":tps}

    def ast_binary_expr(self, stm):
        vals , ops = [], []
        vals.append(self.ast_unary(stm))
        while not stm.eof():
            op = self.ast_try_op(stm)
            if op is None: break
            ops.append(op)
            vals.append(self.ast_unary(stm))
        return {"type":"BIEXPR", "vals":vals, "ops":ops}

    def ast_try_op(stm):
        tkn = stm.peek()
        if tkn.tp is "OP" and tkn.val in Binary:
            return stm.next()
        return None

    def ast_val(self, stm):
        tkn = stm.next()
        if tkn.tp is "LAMBDA":
            val = self.ast_lambda(stm)
        elif tkn.tp is "LIST":
            val = self.ast_list(stream(tkn.val))
        elif tkn.tp is "PARN":
            val = self.ast_parn(stream(tkn.val))
        elif tkn.tp is "DICT":
            val = self.ast_dict(stream(tkn.val))
        elif tkn.tp is "VAR":
            val = {"type":"VAR", "val":tkn.val}
        elif tkn.tp in ('NUM', 'STRING', 'BOOL', "SYSCALL" ,"SYSFUNC", "None"):
            val = {"type":tkn.tp, "val":tkn.val}
        else:
            Error("ast_val")

        return val
            
    def ast_lambda(self, stm):
        stm.next()
        args = self.ast_args(stm)
        syntax_assert(stm.next(), ("OP", "COLON"), "lambda missing :")
        body = self.ast_expr(stm)
        return {"type":"LAMBDA", "args":args, "body":body}

    def ast_list_comp(self, stm):
        beg = self.ast_expr(stm)
        end, interval  = None, 1
        if not syntax_check(stm.peek(), ("OP", "COLON") ):
            stm.next(); end = self.ast_expr(stm)
            if syntax_check(stm.peek(), ("OP", "COLON")):
                stm.next(); interval = self.ast_expr(stm)
        return {"type":"LISTCOM", "beg":beg, "end":end, "interval":interval)
        
    def ast_list(self, stm):
        vals = []
        while not stm.eof():
            vals.append(self.ast_list_comp(stm))
            if not stm.eof():
                syntax_assert(("SEP","COMMA"), stm.next(), "missing comma ,")
        return {"type":"LIST", "val": vals}

    def ast_dict(self, stm):
        key,val = [],[]
        while not stm.eof():
            key.append(self.ast_expr(stm))
            syntax_assert(("OP","COLON"), stm.next(), "missing colon :")
            val.append(self.ast_expr(stm))
            if not stm.eof():
                syntax_assert(("SEP","COMMA"), stm.next(), "missing comma ,")
        return {"type":"DICT", "key":key, "val":val}
        
