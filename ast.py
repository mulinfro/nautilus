from stream import stream
import sys

## Q?   ast_expr   when terminal
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

    def build_ast(self):
        while not self.tokens.eof():
            tkn = self.tokens.peek()
            if tkn.tp is 'DEF':
                self.ast.append(self.ast_def(self.tokens))
            elif tkn.tp is 'IMPORT':
                self.ast.append(self.ast_import(self.tokens))
            else:
                self.ast.append(self.ast_block_expr(self.tokens))

    def ast_import(self, stm):
        syntax_assert(stm.next(), "IMPORT", "", True)
        return ("IMPORT", packages)

    def ast_same_type_seq(self, stm, is_valid):
        tps = []
        tkn = stm.peek()
        while is_valid(tkn):
            tps.append(tkn.val)
            stm.next()
            tkn = stm.peek()
        return tps

    def newlines(self, stm):
        is_valid = lambda tkn: tkn.tp == "NEWLINE"
        vals = self.ast_same_type_seq(stm, is_valid)
        return len(vals) > 0

    def ast_block_expr(self, stm):
        if stm.peek()[0] in ['IF', 'FOR', 'WHILE']:
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
        Error()

    def ast_parn_expr(self, val, checker):
        stm = stream(val)
        vals = self.ast_list(stm)
        checker(stm)
        if len(vals) == 1 and syntax_check(val[-1], ("SEP", "COMMA"), _not = True): 
            return vals[0]
        else:
            return ("TUPLE", tuple(vals))
        
    def check_newline(self, stm):
        if not stm.eof():
            syntax_assert(stm.next().tp, "NEWLINE", False, "syntax error")

    def check_eof(self, stm):
        syntax_assert(stm.eof(), True, False, "syntax error")

    def ast_expr(self, stm, end_checker = self.check_newline):
        true_part, cond, else_part = [], [], []
        true_part = self.ast_binary_expr(stm)
        tkn = stm.peek()
        if tkn.tp is "IF":
            syntax_assert(len(true_part), 0, True, "syntax error")
            stm.next()
            cond = self.ast_binary_expr(stm)
            syntax_assert(stm.next().tp, "ELSE", False, "syntax error")
            else_part = self.ast_binary_expr(stm)
            end_checker(stm)
            return ("SIMPLEIF", [true_part, cond, else_part])

        end_checker(stm)
        return ("BIEXPR", true_part)
                
    def ast_def(self,stm):
        stm.next()
        funcname = self.ast_a_var(stm, "need funcname")
        args = ast_args(stream(stm.next().val))
        body = self.ast_body(self.ast_func_body)
        rt   = self.ast_return()
        self.newlines(stm)
        syntax_assert(stm.next().tp, "END", "missing comma")
        return ('DEF', funcname, args, body)
        
    def ast_args(self, stm, is_end_tkn):
        args, default_args = [], []
        need_default = False
        while not stm.eof():
            arg = self.ast_a_var(stm, "need funcname", True)
            if need_default or stm.looknext():
                syntax_assert(stm.next(), ("ASSIGN", "="), \
                      "non-default argument follows default argument")
                default_value = self.ast_expr(stm)
                default_args.append(( arg, default_value))
                need_default = True

            if not stm.eof():
                syntax_assert(stm.next(), ("SEP","COMMA"), "missing comma")
            if is_end_tkn(tkn):
                return ("ARGS", args, default_args)
        Error("Unexpected EOL")

    def ast_body(self, stm, parse_func = self.ast_func_body):
        body = []
        while not stm.eof():
            if syntax_assert(stm.peek(), ("KEYWORD", "END"))
                stm.next()
                return body
            body.append(parse_func(stm))
       Error() 
    
    def ast_func_body(self, stm):
        tkn = stm.peek()
        if tkn.tp is 'DEF':
            return self.ast_def(stm)
        else:
            return self.ast_block_expr(stm)
        
    def ast_a_var(self, stm, error_msg = "expect a variable", newline = False):
        if newline: self.skip_newline(stm)
        tkn = stm.next()
        syntax_assert(tkn.tp,"VAR", error_msg)
        return tkn.val

    def ast_if(self, stm):
        tkn = stm.next()
        if tkn.tp is not "PARN": Error()
        cond = self.ast_expr(stream(tkn.val), self.check_eof)
        true_part = self.ast_block_expr(stm)
        tkn, else_part = stm.next(), None
        if tkn.tp is "ELSE":
            else_part = self.ast_block_expr(stm)
        if stm.next().tp is not "END": Error()

        self.ast.append(('IF', cond, true_part, else_part)
        
    def ast_pattern_var(self, stm):
        variables = [self.ast_a_var(stm)]
        while True:
            if syntax_check(stm.peek(), ("OP","PATTERN")): 
                stm.next()
                variables.append(self.ast_a_var(stm))
            elif len(variables) > 1: 
                return ("PATTERNVAR", variables)
            else:
                return ("VAR", variables[0])

    def ast_in(self, stm):
        var = self.ast_pattern_var(stm)
        syntax_assert(stm.next(), "IN", "error syntax in for", True)
        val = self.ast_expr(stm)
        return ("IN", var, val)

    def ast_unary(self, stm):
        prefix = self.ast_prefix_op(stm)
        obj_val = self.ast_val(stm)
        suffix = self.ast_suffix_op(stm)
        return ("UNARY", prefix, obj_val, suffix)

    def ast_prefix_op(self, stm):
        is_valid = lambda tkn: tkn.tp is "OP" and tkn.val in Unary
        tps = self.ast_same_type_seq(stm, is_valid)
        return ("PREFIXOP", tps)

    def ast_suffix_op(self, stm):
        is_valid = lambda tkn: tkn.type in ("LIST", "PARN" )
        tps = self.ast_same_type_seq(stm, is_valid)
        return ("SUFFIXOP", tps)

    def ast_binary_expr(self, stm):
        vals , ops = [], []
        while not stm.eof():
            vals.append(self.ast_unary(stm))
            if not stm.eof():
                op = self.ast_try_op(stm)
                if op is None: break
                ops.append(op)
        return ("BINARY", vals, ops)

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
            val = self.ast_tuple(stream(tkn.val))
        elif tkn.tp is "DICT":
            val = self.ast_dict(stream(tkn.val))
        elif tkn.tp in ('NUM', 'STRING', 'BOOL', "SYS_CALL" ,"SYSFUNC"):
            val = (tkn.tp, tkn.val)
        else:
            Error()

        return val
            
            '''
        elif (tkn.tp, tkn.val) == ("OP", "PARTIAL"):
            stm.next()
            t = self.ast_func_call(stm)
            val = ("PARTIAL", t)
            '''
    def ast_lambda(self, stm):
        syntax_assert("LAMBDA", stm.next().tp, "error")
        args = self.ast_args(stm)
        syntax_assert(("OP", "COLON"), stm.next()[0:2], "error")
        body = self.ast_expr(stm)
        return ("LAMBDA", args, body)

    def ast_list_comp(self, stm):
        beg = self.ast_expr(stm)
        if not syntax_check(stm.next(), ("OP", "COLON") ):
            return beg
        end = self.ast_expr(stm)
        interval = 1
        if syntax_check(stm.next(), ("OP", "COLON")):
            interval = self.ast_expr(stm)
        return ("LISTCOM", (beg, end, interval))
        
    def ast_list(self, stm):
        vals = []
        while not stm.eof():
            expr = self.ast_list_comp(stm)
            if not stm.eof():
                syntax_assert(("SEP","COMMA"), stm.next(), "missing comma ,")
            vals.append(expr)
        return ("LIST", vals)

    def ast_tuple(self, stm):
        vals = self.ast_list(stm)
        return ("TUPLE", vals[1])

    def ast_dict(self, stm):
        vals = []
        while not stm.eof():
            key = self.ast_expr(stm)
            syntax_assert(("OP","COLON"), stm.next(), "missing colon :")
            val = self.ast_expr(stm)
            if not stm.eof():
                syntax_assert(("SEP","COMMA"), stm.next(), "missing comma ,")
            vals.append((key, val))
        return ("DICT", vals)
        
    def ast_for(self, stm):
        stm.next()
        tkn = stm.next()
        syntax_assert(tkn.tp, "PARN",  "missing (")
        var, val = self.ast_in(stream(tkn.val))

        body = self.ast_body(self, stm, self.ast_expr)
        return for ("FOR", var, val, body)

    def ast_while(self, stm):
        stm.next()
        tkn = stm.next()
        syntax_assert(tkn.tp, "PARN",  "missing (")
        cond = self.ast_expr(stream(tkn.val))
        body = self.ast_body(self, stm, self.ast_block_expr)
        return ("WHILE", cond, body)
