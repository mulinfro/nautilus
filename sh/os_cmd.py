
import shutil
import os

WORK_DIR = ""
"""
 param: f: files
        d: dirs
"""

def is_file(filename):
    return not os.path.isdir(filename)

def is_dir(path):
    return os.path.isdir(path)

def replace_if_star_dir(path):
    if path[-1] == "*":
        ans = []
        path = path[0:-1]
        for filename in os.listdir(path):
            ans.append(os.path.join(path,filename))
        return ans
    return [path]

def ls(path=".", p=""):
    p = p.lower()
    if "f" not in p and "d" not in p:
        p = p + "df"
    ans = []
    for filename in os.listdir(path):
        new_path = os.path.join(path,filename)
        if os.path.isdir(new_path):
            if "d" in p: ans.append(filename)
            if "r" in p: 
                t = ls(new_path, p)
                joined_t = [ os.path.join(new_path, e) for e in t ]
                ans.extend(joined_t)
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
