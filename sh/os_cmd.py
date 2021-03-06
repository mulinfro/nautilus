
import shutil
import os
from sh.utils import normal_leven
WORK_DIR = ""
"""
 param: f: files
        d: dirs
"""

def is_file(filename):
    return os.path.isfile(filename)

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
        elif "f" in p:
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
    if len(fpath) < 2: return
    if "r" not in p:
        os.remove(fpath)
    else:
        shutil.rmtree(fpath)

def cptree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def cp(src, dst, p=""):
    if "r" in p and is_dir(src):
        cptree(src, dst)
    else:
        shutil.copy2(src, dst)

def mv(src, dst):
    shutil.move(src, dst)


def find(name, dir_path="." , p="r"):
    files = ls(dir_path, p)
    ans = []
    for fn in files:
        head, tail = os.path.split(dir_path)
        dis = normal_leven(tail, name)
        ans.append((dis, fn))
    sorted(ans)
    ans = ans[0:5]
    if len(ans) > 0 and ans[0][1] == 0:
        return [ans[0][1]]
    return list(map(lambda x:x[1], ans))
