from stream import stream


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
            cur_tkn = stm.peek()
            if cur_tkn[0] in ['IF', 'FOR', 'WHILE']:
                self.ast.append(self.ast_control(self.tokens))
            else:
                self.ast.append(self.ast_binary_expr(self.tokens))
            

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
            
            





                

        
