"""
     将tokens转化成ast; 加上一定的语法检查
     一个ast节点用字典表示，字典中包含了解析此node的必要信息
"""
from stream import stream
from syntax_check import *
from builtin import Binary, Unary
import sys

Tautology = lambda x: True

# 分隔符语法检查
def check_expr_end(stm):
    if not stm.eof():
        syntax_assert(stm.next(), "SEP", "syntax error")

def check_newline(stm):
    if not stm.eof():
        syntax_assert(stm.next(), ("SEP", "NEWLINE"), "syntax error")

def check_comma(stm):
    if not stm.eof():
        syntax_assert(stm.next(), ("SEP", "COMMA"), "syntax error")

def check_eof(stm):
    syntax_cond_assert(stm.eof(), "syntax error")

class AST():
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.ast = []
        self.build_ast()

    def build_ast(self):
        while True:
            self.newlines(self.tokens)
            if self.tokens.eof(): break
            tkn = self.tokens.peek()
            if tkn.tp is 'DEF':
                val = self.ast_def(self.tokens)
            elif tkn.tp in ["FROM", 'IMPORT']:
                val = self.ast_import(self.tokens)
            elif tkn.tp in ['IF', 'FOR', 'WHILE']:
                val = self.ast_control(self.tokens)
            else:
                val = self.ast_try_pattern_assign(self.tokens)

            self.ast.append(val)

    def ast_assign_helper(self, stm, tps):
        tkn = self.tokens.peek()
        if tkn.tp is "VAR" and not stm.eof() and stm.looknext().tp in tps:
            var = self.ast_pattern_var(stm)
            a_tp = stm.next().tp
            val = self.ast_try_assign(stm)
            return {"type":a_tp, "var":var, "val":val}
        return None

    # 模式匹配赋值 example  x::y::_ = [1,2,3]  => x=1, y=2, _ = [3]
    def ast_try_pattern_assign(self, stm):
        t = self.ast_assign_helper(stm, ("PASSIGN", ))
        return self.ast_try_assign(stm) if t is None else t

    # 赋值；可连续赋值 x=y=z=1+1
    def ast_try_assign(self, stm):
        t = self.ast_assign_helper(stm, ("ASSIGN", "GASSIGN"))
        if t is None:
            t = self.ast_expr(stm)
            check_expr_end(stm)
        return t
        
    def ast_import(self, stm):
        _from, _import, _as = "", [], []
        parent_dir_num = -1

        def ast_dots():
            module  = [ self.ast_a_var(stm)["name"] ]
            while not stm.eof():
                if stm.peek().tp != "DOT": break
                module.append(self.ast_dot(stm)["attribute"])
            return module

        def seq_ast_dots(seq):
            while True:
                seq.append(ast_dots())
                if stm.eof() or not syntax_check(stm.peek(), ("SEP", "COMMA")):
                    break

        if stm.peek().tp == "FROM":
            stm.next()
            while stm.peek().tp == "DOT":
                stm.next()
                parent_dir_num = parent_dir_num + 1
            _from = ast_dots()
        syntax_assert(stm.next(), "IMPORT") 
        seq_ast_dots(_import)

        if stm.peek().tp == "AS":
            seq_ast_dots(_as)
        if not stm.eof():
            syntax_assert(stm.next(), ("SEP", "NEWLINE"))
            
        return {"type":"IMPORT", "p_num": parent_dir_num, 
                "from":_from, "import":_import, "as":_as}

    def ast_same_type_seq(self, stm, is_valid):
        tps = []
        while not stm.eof() and is_valid(stm.peek()):
            tps.append(stm.next().val)
        return tps

    def newlines(self, stm):
        is_valid = lambda tkn: syntax_check(tkn, ("SEP","NEWLINE"))
        vals = self.ast_same_type_seq(stm, is_valid)
        return len(vals) > 0

    def ast_block_expr(self, stm):
        if stm.peek().tp in ['IF', 'FOR', 'WHILE']:
            return self.ast_control(stm)
        elif stm.peek().tp in ["BREAK", "CONTINUE"]:
            return self.ast_bc(stm)
        elif stm.peek().tp == "RETURN":
            return self.ast_return(stm)
        else:
            return self.ast_try_pattern_assign(stm)

    def ast_bc(self, stm):
        tp = stm.next().tp
        check_newline(stm)
        return {"type": tp}

    def ast_return(self, stm):
        stm.next()
        expr = self.ast_expr(stm)
        check_newline(stm)
        return {"type": "RETURN", "rval": expr}

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
        default_args, default_vals = [], []
        is_tuple, is_assign, is_partial = False, False, False
        while not stm.eof():
            t = self.ast_try_assign(stm)
            syntax_cond_assert( t["type"] is not "GASSIGN", "syntax error unexpected global assign")
            if is_assign:
                syntax_cond_assert( t["type"] is "ASSIGN", "error undefault args follow default args")

            if t["type"] == "VAR" and t["name"] == "_":
                is_partial = True
            if t["type"] is "ASSIGN":
                is_assign = True
                syntax_cond_assert(t["val"]["type"] != "ASSIGN", "unexpected continue assign")
                default_args.append(t["var"]["name"])
                default_vals.append(t["val"])
            else:
                vals.append(t)
        if is_assign or is_partial:
            tp = "ARGS" if not is_partial else "PARTIAL"
            return {"type":tp, "val":vals, 
                 "default_args": default_args, "default_vals":default_vals}
        elif len(vals) != 1:
            return {"type":"TUPLE", "val":vals}
        else:
            return {"type":"PARN", "val":vals}
                

    def ast_expr(self, stm):
        true_part = self.ast_binary_expr(stm)
        if not stm.eof() and stm.peek().tp is "IF":
            stm.next()
            cond = self.ast_binary_expr(stm)
            syntax_assert(stm.next(), "ELSE", "need else branch")
            else_part = self.ast_binary_expr(stm)
            return {"type":"SIMPLEIF", "then":true_part,
                    "cond":cond, "else":else_part}

        return true_part
                
    def ast_def(self, stm):
        stm.next()
        funcname = self.ast_a_var(stm, "need funcname")
        args = self.ast_args(stm)
        body = self.ast_body(stm, self.ast_func_body)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":'DEF', "funcname":funcname["name"], 
                "args":args, "body":body}
        
    def ast_args(self, stm):
        syntax_assert(stm.peek(), "PARN", "need parenthese")
        t = self.ast_parn(stream(stm.next().val))
        t["type"] = "ARGS"
        return t

    def ast_body(self, stm, parse_func):
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
        syntax_assert(tkn, "VAR", error_msg)
        return {"type":"VAR", "name":tkn.val}

    def ast_if(self, stm):
        stm.next(); tkn = stm.next()
        syntax_assert(tkn, "PARN", "need parn")
        cond_stream = stream(tkn.val)
        cond = self.ast_expr(cond_stream)
        check_eof(cond_stream)
        true_part = self.ast_body(stm, self.ast_block_expr)
        tkn, else_part = stm.peek(), None
        if tkn.tp is "ELSE":
            else_part = self.ast_body(stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":'IF', "cond":cond, "then":true_part, "else":else_part}
        
    def ast_for(self, stm):
        stm.next(); tkn = stm.next()
        syntax_assert(tkn, "PARN",  "missing (")
        _in = self.ast_in(stream(tkn.val))
        body = self.ast_body(stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":"FOR", "in":_in, "body":body}

    def ast_while(self, stm):
        stm.next(); tkn = stm.next()
        syntax_assert(tkn.tp, "PARN",  "missing (")
        cond_stream = stream(tkn.val)
        cond = self.ast_expr(cond_stream)
        check_eof(cond_stream)
        body = self.ast_body(self, stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":"WHILE", "cond":cond, "body":body}

    def ast_pattern_var(self, stm):
        variables = [self.ast_a_var(stm)]
        while syntax_check(stm.peek(), "PASSIGN"):
            stm.next()
            variables.append(self.ast_a_var(stm)["name"])

        if len(variables) > 1: 
            return {"type":"PATTERNVAR", "variables":variables}
        else:
            return variables[0]

    def ast_in(self, stm):
        var = self.ast_pattern_var(stm)
        syntax_assert(stm.next(), ("OP", "IN"), "syntax error in for setence")
        val = self.ast_expr(stm)
        check_eof(stm)
        return {"type":"IN", "var":var, "val":val }

    def ast_unary(self, stm):
        prefix = self.ast_prefix_op(stm)
        obj_val = self.ast_val(stm)
        suffix = self.ast_suffix_op(stm)
        if len(prefix["val"]) + len(suffix["val"]) == 0: return obj_val
        return {"type":"UNARY", "prefix":prefix["val"],
                "obj":obj_val, "suffix":suffix["val"]}

    def ast_prefix_op(self, stm):
        is_valid = lambda tkn: tkn.tp is "OP" and tkn.val in Unary
        tps = self.ast_same_type_seq(stm, is_valid)
        return {"type":"PREFIXOP", "val":tps}

    def ast_suffix_op(self, stm):
        tps = []
        while not stm.eof():
            tp = stm.peek().tp 
            if tp in ("LIST", "PARN", "TUPLE" ):
                tps.append(self.ast_val(stm))
            elif tp is "DOT":
                tps.append(self.ast_dot(stm))
            else:
                break
        return {"type":"SUFFIXOP", "val":tps}

    def ast_dot(self, stm):
        stm.next()
        var = self.ast_a_var(stm)
        return {"type":"DOT", "attribute": var["name"]}

    def ast_binary_expr(self, stm):
        vals , ops = [], []
        vals.append(self.ast_unary(stm))
        while not stm.eof():
            op = self.ast_try_op(stm)
            if op is None: break
            ops.append(op)
            vals.append(self.ast_unary(stm))
        if len(ops) == 0: return vals[0]
        else: return {"type":"BIEXPR", "val":vals, "op":ops}

    def ast_try_op(self, stm):
        tkn = stm.peek()
        if tkn.tp is "OP" and tkn.val in Binary:
            return {"type":tkn.tp, "val":stm.next().val}
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
            val = {"type":"VAR", "name":tkn.val}
        elif tkn.tp in ('NUM', 'STRING', 'BOOL', "SYSCALL" ,"SYSFUNC", "NONE"):
            val = {"type":tkn.tp, "val":tkn.val}
        else:
            Error("Parse Error:%s,%s"%(tkn.tp, str(tkn.val)), tkn.line, tkn.col)

        return val
            
    def ast_lambda(self, stm):
        args = self.ast_args(stm)
        syntax_assert(stm.next(), ("OP", "COLON"), "lambda missing :")
        body = self.ast_expr(stm)
        return {"type":"LAMBDA", "args":args, "body":body}

    def ast_list_comp(self, stm):
        beg = self.ast_expr(stm)
        end, interval  = None, 1
        if not stm.eof() and syntax_check(stm.peek(), ("OP", "COLON") ):
            stm.next(); end = self.ast_expr(stm)
            if not stm.eof() and syntax_check(stm.peek(), ("OP", "COLON")):
                stm.next(); interval = self.ast_expr(stm)
        check_comma(stm)
        if end is None: return beg
        return {"type":"LISTCOM", "beg":beg, "end":end, "interval":interval}
        
    def ast_list(self, stm):
        vals = []
        while not stm.eof():
            vals.append(self.ast_list_comp(stm))
        return {"type":"LIST", "val": vals}

    def ast_dict(self, stm):
        key,val = [],[]
        while not stm.eof():
            key.append(self.ast_expr(stm))
            syntax_assert(stm.next(), ("OP","COLON"),  "missing colon :")
            val.append(self.ast_expr(stm))
            check_comma(stm)
        return {"type":"DICT", "key":key, "val":val}
