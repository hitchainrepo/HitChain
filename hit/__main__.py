# -- coding: utf-8 --
import sys
import os
import random
import string
import time
from .classmodule import RemoteRepo
from .funcmodule import *


def main():
    args = sys.argv[1:]
    # print args
    if args[0] == 'push':
        projectLocation = os.getcwd()
        remoteRepo = RemoteRepo()
        # 获取远程地址
        remoteHash = remoteRepo.getRemoteHash()
        remoteUrl = remoteRepo.getRemoteUrl()
        # 远程仓库在本地的存放位置
        pathLocalRemoteRepo = genKey32()
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

    elif args[0] == "transfer":
        if args[1][0:4] == "http":
            repoName = args[1].split("/")[-1]
            os.system("git clone --bare %s" % (args[1]))
            projectLocation = os.getcwd()
            os.chdir(repoName)
            os.system("git update-server-info")
            os.system("echo " + repr(time.time()) + " > timestamp")  # 生成一个时间戳文件
            newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
            remoteHash = os.popen("ipfs key gen --type=rsa --size=2048 %s" % repoName).read()
            namePublishCmd = "ipfs name publish --key=%s %s" % (repoName, newRepoHash)
            os.system(namePublishCmd)
            os.system("rm -rf %s/%s" % (projectLocation, repoName))
        elif len(args) == 1:
            # 将本地的版本库上传
            repoName = args[1].split("/")[-1]
            # 改成将本地库改成bare库
            # os.system("git clone --bare %s" % (args[1]))
            projectLocation = os.getcwd()
            os.chdir(repoName)
            os.system("git update-server-info")
            newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
            remoteHash = os.popen("ipfs key gen --type=rsa --size=2048 %s" % repoName).read()
            namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash, newRepoHash)
            os.system(namePublishCmd)
            return


    else:
        cmd = "git"
        for arg in args:
            cmd += " " + arg
        os.system(cmd)
    
if __name__ == '__main__':
    main()

