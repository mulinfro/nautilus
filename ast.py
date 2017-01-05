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
            args = []
            while not stm.eof():
                if len(args) > 0:
                    syntax_assert(stm.next()[1], "COMMA", "missing comma")
                args.append(ast_one_arg)
            return args


        def ast_one_arg(self, stm):
            arg = self.ast_a_var(stm, "need funcname", True)
            tkn_type, tkn_val = stm.peek()
            default_value = []
            if tkn_type is "ASSIGN":
                stm.next()
                default_value.append(self.ast_binary_expr(stm))
            return (arg, default_value)

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
            pass


            
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

