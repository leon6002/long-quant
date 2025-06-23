import os
import sys

cur_dir = os.getcwd()
print(f'cur_dir is: {cur_dir}')
pkg_rootdir = os.path.dirname(os.path.dirname(cur_dir))
src_dir = os.path.join(pkg_rootdir, 'src')
if pkg_rootdir not in sys.path:
    sys.path.append(pkg_rootdir)
if src_dir not in sys.path:
    sys.path.append(src_dir)