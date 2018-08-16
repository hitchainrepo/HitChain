import sys
import os
from .classmodule import RemoteRepo
# from .funcmodule import my_function


def main():
    args = sys.argv[1:]
    print args
    if args[0] == 'push':
        remoteRepo = RemoteRepo()
        # 获取远程地址
        remoteHash = remoteRepo.getRemoteHash()
        remoteUrl = remoteRepo.getRemoteUrl()
        # 获取远程仓库：ipfs get 远程地址
        ipfsGetRepoCmd = "ipfs get %s" % remoteHash # 要重命名
        os.system(ipfsGetRepoCmd)
        # 将版本库提交到本地仓库
        pathLocalRemoteRepo = "" # 远程仓库在本地的存放位置
        gitPushCmd = "git push %s" % (pathLocalRemoteRepo)
        for arg in args[1:]:
            gitPushCmd += " " + arg # 这里注意，如果用户添加了地址，这里没有去除
        os.system(gitPushCmd)
        # 获取远程仓库的时间戳remoteTimeStamp
        remoteTimeStamp = "ipfs get %s/timestamp" % remoteHash
        if RemoteRepo.timeStamp == remoteTimeStamp:
            # 在仓库中添加本地的时间戳
            # 将合并后的代码仓库提交到ipfs网络中: ipfs add -r
            os.system("ipfs add -r") # 要进入仓库路径中
            # 获取新提交的仓库rootFileUrl，并将其命名到名字空间中
        else:
            print "Err: The remote repo has been updated by other user, please push the repo again"

        # 删除本地的远程仓库
        os.system("rm -rf %s" % pathLocalRemoteRepo)

    else:
        cmd = "git"
        for arg in args:
            cmd += " " + arg
        os.system(cmd)
    
if __name__ == '__main__':
    main()

