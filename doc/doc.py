# 预先存在文件结构
# ./doc
# ./doc/rst/
# ./doc/html/

if __name__ == '__main__':
    import os, sys

    # os.system('sphinx-quickstart') # 中选择> Root path for the documentation [.]: ./rst

    os.system('sphinx-apidoc -o ./rst/source ../')  # sphinx-apidoc -o [conf.py所在目录] [源码目录]

    sys.path.insert(0, os.path.abspath('../'))  # 在运行文档生成脚本之前，要确保你的Python源代码所在的包在系统路径中是可以找到的
    os.system('sphinx-build -b html ./rst/source ./html')  # sphinx-build -b html [conf.py所在目录] [生成html目录]
