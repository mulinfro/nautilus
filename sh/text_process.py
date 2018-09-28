
import re
from itertools import chain
from sh.os_cmd import is_dir, replace_if_star_dir

def pipe_itertool(func):
    def wrapper(*args, **kw):
        assert(len(args) > 0)
        if type(args[0]) == str:
            return func(*args, **kw)
        for line in args[0]:
            new_args = (line,) + args[1:]
            ans = func(*new_args, **kw)
            if ans is not None: yield ans
    return wrapper
    
@pipe_itertool
def grep(line, pat, p=""):
    if pat in line: return line

def wc(iterable, p="l"):
    i = 0
    for x in iterable:
        i += 1
    return i

@pipe_itertool
def egrep(line, pat, p="i"):
    if "i" in p: pattern = re.compile(pat, re.I)
    else:        pattern = re.compile(pat)
    match = pattern.search(line)
    if match:
        return line

@pipe_itertool
def replace(line, pat, repl, p="", cnt=0):
    if "v" not in p:
        return line.replace(pat, repl)
    else:
        return re.replace(pat, repl, line, cnt)


def cat(iterable):
    if type(iterable) == str: iterable = [iterable]
    for path in iterable:
        pathes = replace_if_star_dir(path)
        for file_name in pathes:
            if is_dir(file_name): continue
            f = open(file_name, "r")
            for line in f:
                yield line
            f.close()

@pipe_itertool
def tojson(line):
    import json
    return json.loads(line.strip())

def more(file_name):
    f = open(file_name, "r")
    i = 0
    for line in f:
        yield line
        i += 1
        if i % 10 ==0:
            is_continue = input("more? ")
            if is_continue not in ["", "y", "Y"]: break
    f.close()

def groupby():
    pass

def xreduce(iterable):
    pass

def head(iterable, n=10):
    i = 0
    for line in iterable:
        i += 1
        if i > n: break
        yield line

def awk():
    pass

def flat(listOfLists):
    return chain.from_iterable(listOfLists)

def flatMap(f, items):
    return chain.from_iterable(map(f, items))

def join():
    pass

def xmap(eles, func = lambda x:x):
    return [func(x) for x in eles]

def sed():
    pass

@pipe_itertool
def split(string, sep="", cnt=0, p=""):
    if "v" in p:
        return re.split(sep, string, cnt)
    else:
        return string.split(sep, cnt)

def findall():
    pass

def search():
    pass

def xsort(lines, n=-1, f="", p=""):
    pass

def uniq(iterable):
    pass
