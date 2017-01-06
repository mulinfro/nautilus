from stream import stream

def syntax_assert(tkn, need_tkn, errstr = "", not_ = False):
    flag = tkn == need_tkn 
    if not_: flag = not flag
    if not flag and error_msg: Error(error_msg)
    return True

class AST():
    
    def __init__(self, tokens):
        self.tokens = stream(tokens)
        self.ast = []


    def build_ast(self):
        while not self.tokens.eof():
            cur_tkn = self.tokens.peek()
            next_tkn = self.tokens.looknext()
            if cur_tkn[0] is 'DEF':
                self.ast.append(self.ast_def(self.tokens))
            elif cur_tkn[0] in ['IF', 'FOR', 'WHILE']:
                self.ast.append(self.ast_control(self.tokens))
            elif cur_tkn[0] is 'IMPORT':
                self.ast.append(self.ast_import(self.tokens))
            else:
                self.ast.append(self.ast_binary_expr(self.tokens))


        def ast_control(self):
            cur_tkn = self.tokens.peek()
            if cur_tkn[0] is 'IF':
                self.ast.append(self.ast_if())
            elif cur_tkn[0] is 'FOR':
                self.ast.append(self.ast_for())
            elif cur_tkn[0] is 'WHILE':
                self.ast.append(self.ast_while())

        def ast_exprs(self, stm):
            while True:
                cur_tkn = stm.peek()
                if cur_tkn[0] in ['IF', 'FOR', 'WHILE']:
                    self.ast.append(self.ast_control(self.tokens))
                else:
                    self.ast.append(self.ast_binary_expr(self.tokens))
                
        def ast_def(self,stm):
            stm.next()
            funcname = self.ast_a_var(stm, "need funcname")
            cur_tkn = stm.next()
            args = ast_args(stream(cur_tkn[1]))
            body = ast_body()
            return ('DEF', funcname, args, body)
            
        def ast_args(self, stm):
            args, default_args = [], []
            need_default = False
            while not stm.eof():
                if not need_default and stm.leftnum() > 1 and syntax_assert(stm.looknext(), ("SEP", "COMMA")):
                    args.append(self.ast_one_arg(stm))
                else:
                    need_default = True
                    default_args.append(self.ast_one_default_arg(stm))

                if not stm.eof():
                    syntax_assert(stm.next(), ("SEP","COMMA"), "missing comma")
            return ("ARGS", args, default_args)


        def ast_one_arg(self, stm):
            arg = self.ast_a_var(stm, "need funcname", True)
            return ("ARG", arg)

        def ast_one_default_arg(self, stm):
            arg = self.ast_a_var(stm, "syntax error")
            syntax_assert(stm.next(), ("ASSIGN", "="), \
                  "non-default argument follows default argument")
            default_value = self.ast_binary_expr(stm)
            return ("DEFAULT_ARG", arg, default_value)

        def ast_body(self, stm, parse_func = self.ast_body_part):
            body = []
            while not stm.eof():
                if syntax_assert(stm.peek(), ("KEYWORD", "END"))
                    stm.next()
                    return body
                body.append(self.ast_body_part(stm))
           Error() 
        
        def ast_body_part(self, stm):
            tkn_type, tkn_val = stm.peek()
            syntax_assert(tkn_type != 'IMPORT')
            if tkn_type is 'DEF':
                return self.ast_def(stm)
            else:
                return self.ast_exprs(stm)
            
        def ast_a_var(self, stm, error_msg = "expect a variable", newline = False):
            if newline: self.skip_newline(stm)
            tkn_type, tkn_val = stm.next()
            syntax_assert(cur_tkn[0],"VAR", error_msg)
            return tkn_val

        def skip_newline(self, stm):
            while not stm.eof() and stm.peek()[1] is "NEWLINE":
                stm.next()
            
        def ast_if(self, stm):
            cur_tkn = stm.next()
            if cur_tkn[0] is not "PARN": error()
            cond = self.ast_binary_expr(stream(cur_tkn[1]))
            true_part = self.ast_exprs(stm)
            cur_tkn = self.tokens.peek()
            else_part = None
            if cur_tkn[0] is "ELSE":
                else_part = self.ast_exprs()
                cur_tkn = self.tokens.peek()
            if cur_tkn[0] is not "END": error()
            self.tokens.next()

            self.ast.append(('IF', cond, true_part, else_part)
            
        def ast_pattern_var(self, stm):
            variables = []
            while True:
                variables.append(ast_a_var(self, stm))
                tkn_type, tkn_val = stm.peek()
                if check_token(): stm.next()
                else: return variables

        def ast_in(self, stm):
            vars = self.ast_pattern_var(stm)
            syntax_assert(stm.next(), ("KEYWORD", "IN"), "error syntax in for")
            val = self.ast_binary_expr(stm)
            return ("IN", vars, val)

        def ast_binary_expr(self, stm):
            vals , ops = [], []
            while not stm.eof():
                tkn_type, tkn_val = stm.peek()
                if tkn_type is "PARN":
                    vals.append(self.ast_binary_expr(stream(tkn_val)))
                else:
                    vals.append(self.ast_prefix_expr(stm))
                if not stm.eof():
                    tkn_type, tkn_val = stm.peek()
                    if tkn_type is "IF":
                        return self.ast_simple_if(stm, ("BINARY", vals, ops))
                    op = self.ast_op(stm)
                    if op is None: return ("BINARY", vals, ops)
                    ops.append(op)

        def ast_prefix_expr(self, stm):
            tkn_type, tkn_val = stm.peek()
            op = self.ast_op(stm)
            if op not in Unary: Error()
            return ("PREFIX", op, self.ast_val_expr(stm))

            
        def ast_val_expr(self, stm):
            tkn_type, tkn_val = stm.peek()
            if tkn_type is "LIST":
                self.ast_list(stream(stm))
            elif tkn_type is "PARN":
                self.ast_parn(stream(stm))
            elif tkn_type is "DICT":
                self.ast_dict(stream(stm))
            elif tkn_type is "LAMBDA":
                self.ast_lambda(stm)
            elif (tkn_type, tkn_val) == ("OP", "PARTIAL"):
                stm.next()
                t = self.ast_func_call()
                val = ("PARTIAL", t)
            else:

            return val
                

        def ast_lambda(self, stm):
            stm.next()
            args = self.ast_args(stm)
            syntax_assert(("OP", "COLON"), stm.next(), "error")
            body = self.ast_binary_expr(stm)
            return ("LAMBDA", args, body)

        def ast_
            
        def ast_list_comp(self, stm):
            beg, end, interval = 0,0,1
            beg = self.ast_binary_expr()
            syntax_assert(("OP", "COLON"), stm.next()):
            end = self.ast_binary_expr()
            if syntax_assert(("OP", "COLON"), stm.next()):
                interval = self.ast_binary_expr()
            return ("LISTCOM", (beg, end, interval))
            
        def ast_list(self, stm):
            vals = []
            while not stm.eof():
                if syntax_assert(("OP", "COLON"), stm.looknext()):
                    expr = self.ast_list_comp(stm)
                else:
                    expr = self.ast_binary_expr()
                if not stm.eof():
                    syntax_assert(("SEP","COMMA"), stm.next(), "missing comma ,")
                vals.append(expr)
            return ("LIST", vals)

        def ast_tuple(self, stm):
            pass

        def ast_dict(self, stm):
            vals = []
            while not stm.eof():
                key = self.ast_binary_expr(stm)
                syntax_assert(("OP","COLON"), stm.next(), "missing colon :")
                val = self.ast_binary_expr(stm)
                if not stm.eof():
                    syntax_assert(("SEP","COMMA"), stm.next(), "missing comma ,")
                vals.append((key, val))
            return ("DICT", vals)
            
        def ast_for(self, stm):
            stm.next()
            tkn_type, tkn_val = stm.next()
            syntax_assert(tkn_type, "PARN",  "missing (")
            vars, val = self.ast_in(stream(tkn_val))

            body = self.ast_body(self, stm, self.ast_exprs)
            return for ("FOR", vars, val, body)

        def ast_while(self, stm):
            stm.next()
            tkn_type, tkn_val = stm.next()
            syntax_assert(tkn_type, "PARN",  "missing (")
            cond = self.ast_binary_expr(stream(tkn_val))
            body = self.ast_body(self, stm, self.ast_exprs)
            return ("WHILE", cond, body)

