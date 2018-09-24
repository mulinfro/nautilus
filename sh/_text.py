
import re
from itertools import imap, chain

def grep(pattern, iterable, p="ir"):
    for line in iterable:

    pass

def replace(iterable, pre="", now="", p=""):
    for line in iterable:
        if r not in p:
            yield line.replace(pre, now)
        else:
            yield re.place(line, pre, now)

def cat(iterable):
    for file_name in iterable:
        f = open(file_name, "r")
        for line in f.readline():
            yield line
        f.close()

def more(file_name):
    f = open(file_name, "r")
    while True:
        ans = []
        for i in range(10):
            ans.append(f.readline())
        yield ans
        is_continue = input("more? ")
        if is_continue in ["", "y", "Y"]: break
    f.close()

def groupby():
    pass

def xreduce(iterable):
    pass

def head(iterable, n=10):
    i = 0
    ans = []
    for line in iterable:
        i += 1
        if i > n: break
        ans.append(line)
    return ans

def awk():
    pass

def flat(listOfLists):
    return chain.from_iterable(listOfLists)

def flatMap(f, items):
    return chain.from_iterable(imap(f, items))

def join():
    pass

def xmap(eles, func = lambda x:x):
    return [func(x) for x in eles]

def sed():
    pass

def split(string, sep="", maxsplit=0, p=""):
    if "v" in p:
        return re.split(pattern, string, maxsplit)
    return string.split(pattern)

def findall():
    pass

def xsort(lines, n=-1, f="", p=""):
    pass

def uniq(iterable):
    pass
