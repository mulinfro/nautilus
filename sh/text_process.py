
import re
from itertools import chain
from os_cmd import is_dir, replace_if_star_dir

def grep(pattern, iterable, p="ir"):
    for line in iterable:
        if pattern in line:
            yield line

def replace(iterable, pat="", repl="", p="", cnt=0):
    for line in iterable:
        if "v" not in p:
            yield line.replace(pat, repl)
        else:
            yield re.replace(pat, repl, line, cnt)

def cat(iterable):
    for path in iterable:
        pathes = replace_if_star_dir(path)
        for file_name in pathes:
            if is_dir(file_name): continue
            f = open(file_name, "r")
            for line in f.readline():
                yield line
            f.close()

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

def split(string, sep="", cnt=0, p=""):
    if "v" in p:
        return re.split(pattern, string, cnt)
    return string.split(pattern, cnt)

def findall():
    pass

def search():
    pass

def xsort(lines, n=-1, f="", p=""):
    pass

def uniq(iterable):
    pass
