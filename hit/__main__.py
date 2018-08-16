import sys
import os
from .classmodule import RemoteRepo
# from .funcmodule import my_function


def main():
    args = sys.argv[1:]
    print args
    if args[0] == 'push':
        remoteRepo = RemoteRepo()
        remoteUrl =
        # 获取远程地址
        # 获取远程仓库：ipfs get 远程地址
        # 将版本库提交到本地仓库
        remoteTimeStamp = '' # 获取远程仓库的时间戳remoteTimeStamp
        if RemoteRepo.timeStamp == remoteTimeStamp:
        #     在仓库中添加本地的时间戳
        #     将合并后的代码仓库提交到ipfs网络中: ipfs add -r
        # 获取新提交的仓库rootFileUrl，并将其命名到名字空间中
        else:
            print "Err: The remote repo has been updated by other user, please push the repo again"

    else:
        cmd = "git"
        for arg in args:
            cmd += " " + arg
    	os.system(cmd)
    
if __name__ == '__main__':
    main()

