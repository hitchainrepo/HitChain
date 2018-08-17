# -- coding: utf-8 --
import sys
import os
import random
import string
import time
from .classmodule import RemoteRepo
from .funcmodule import gitPushExchange


def main():
    args = sys.argv[1:]
    print args
    if args[0] == 'push':
        projectLocation = os.getcwd()
        remoteRepo = RemoteRepo()
        # 获取远程地址
        remoteHash = remoteRepo.getRemoteHash()
        remoteUrl = remoteRepo.getRemoteUrl()
        # 远程仓库在本地的存放位置
        pathLocalRemoteRepo = ''.join(random.sample(string.ascii_letters + string.digits, 32))
        # 获取远程仓库：ipfs get 远程地址
        ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteUrl,pathLocalRemoteRepo) # 要重命名
        os.system(ipfsGetRepoCmd)
        # 将版本库提交到本地仓库
        gitPushCmd = "git push %s" % (pathLocalRemoteRepo)
        for arg in args[1:]:
            gitPushCmd += " " + arg # 这里注意，如果用户添加了地址，这里没有去除
        os.system(gitPushCmd)
        # 获取远程仓库的时间戳remoteTimeStamp
        remoteTimeStamp = "ipfs cat %s/timestamp" % remoteUrl
        if RemoteRepo.timeStamp == remoteTimeStamp:
            os.chdir(pathLocalRemoteRepo)
            # 在仓库中添加本地的时间戳
            os.system("echo " + repr(time.time()) + " > timestamp") # 生成一个时间戳文件
            # 将合并后的代码仓库提交到ipfs网络中: ipfs add -r
            newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
            # 获取新提交的仓库rootFileUrl，并将其命名到名字空间中
            namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash,newRepoHash)
            os.system(namePublishCmd)
        else:
            print "Err: The remote repo has been updated by other user, please push the repo again"

        # 删除本地的远程仓库
        os.chdir(projectLocation)
        os.system("rm -rf %s" % pathLocalRemoteRepo)

    else:
        cmd = "git"
        for arg in args:
            cmd += " " + arg
        os.system(cmd)
    
if __name__ == '__main__':
    main()

