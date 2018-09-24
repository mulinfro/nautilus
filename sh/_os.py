
import shutil
import os

WORK_DIR = ""
"""
 param: f: files
        d: dirs
"""

def replace_if_star_dir(path):
    if path[-1] == "*":
        ans = []
        path = path[0:-1]
        for filename in os.listdir(path):
            ans.append(os.path.join(path,filename))
        return ans
    else:
        return path

def ls(path="", p=""):
    p = p.lower()
    if ("f" in p and "d" in p) or ("f" not in p and "d" not in p):
        return os.listdir(path)
    ans = []
    for filename in os.listdir(path):
        if os.path.isdir(os.path.join(path,filename)):
            if "d" in p: ans.append(filename)
        elif "f" in P:
            ans.append(filename)

    return ans

def ll():
    pass

def pwd():
    return os.getcwd()

def cd(path = ".."):
    os.chdir(path)

def mkdir(path):
    os.mkdir(path)

def rm(fpath, p=""):
    if "r" not in p:
        os.remove(fpath)
    else:
        shutil.rmtree(fpath)

def cp():
    pass

def mv():
    pass

def find(name, dir_path="." , p="r"):
    pass
