# syntax check help functions


def Error(msg, tkn=None):
    if tkn:
        print("Syntax Error: In line %d Col %d %s" % (tkn.line,tkn.col, msg), file=sys.stderr)
    raise Exception("ASTERROR")

def syntax_check(tkn, need_tkn, not_ = False):
    if type(need_tkn) is tuple: flag = (tkn.tp, tkn.val) == need_tkn 
    else:      flag = tkn.tp == need_tkn 
    return not flag if not_ else flag

def syntax_assert(tkn, need_tkn,  errstr = "", not_ = False):
    if not syntax_check(tkn, need_tkn, not_):
        print(tkn, need_tkn)
        Error(errstr)
    return True

def syntax_cond_assert(cond,  errstr = "", not_ = False):
    if not cond: Error(error_msg)
    return True
