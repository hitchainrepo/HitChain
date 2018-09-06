# -- coding: utf-8 --
import sys
import os
# import random
# import string
import time
from .classmodule import RemoteRepo, AccessControl
from .funcmodule import *


def main():
    args = sys.argv[1:]
    # print args
    if args[0] == 'push':
        projectLocation = os.getcwd()
        remoteRepo = RemoteRepo()
        # 获取远程地址
        remoteHash = remoteRepo.getRemoteHash()
        # remoteUrl = remoteRepo.getRemoteUrl()
        remoteFileHash = remoteRepo.getRemoteFileHash()

        # 获取权限文件
        os.system("ipfs get %s/%s" % (remoteFileHash,remoteHash))
        accessControl = AccessControl(remoteHash)
        accessControl.setKeyNameFromJson()
        accessControl.getUserKey("self")
        # 有权限则继续
        if accessControl.verifiAuth(accessControl.pubkey):
            # 远程仓库在本地的存放位置
            pathLocalRemoteRepo = genKey32()
            # 获取远程仓库：ipfs get 远程地址
            print "hit get ipfs repo to local"
            ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteFileHash,pathLocalRemoteRepo) # 要重命名
            print ipfsGetRepoCmd
            os.system(ipfsGetRepoCmd)
            # 将版本库提交到本地仓库
            print "hit push to local"
            gitPushCmd = "git push %s" % (pathLocalRemoteRepo)
            for arg in args[1:]:
                gitPushCmd += " " + arg # 这里注意，如果用户添加了地址，这里没有去除
            os.system(gitPushCmd)
            # 获取远程仓库的时间戳remoteTimeStamp
            print "compare local repo with remote repo"
            remoteTimeStamp = os.popen("ipfs cat %s/timestamp" % remoteFileHash).read()
            if remoteRepo.timeStamp == remoteTimeStamp:
                os.chdir(pathLocalRemoteRepo)
                # 在仓库中添加本地的时间戳
                os.system("git update-server-info")
                os.system("echo " + repr(time.time()) + " > timestamp") # 生成一个时间戳文件
                # 将合并后的代码仓库提交到ipfs网络中: ipfs add -r
                print "add repo to ipfs network"
                newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
                # 获取新提交的仓库rootFileUrl，并将其命名到名字空间中
                accessControl.savePublicKeyOfIpns(accessControl.getPublicKeyFromJson())
                print "publish file to ipns %s" % remoteHash
                namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash,newRepoHash)
                os.system(namePublishCmd)
                accessControl.deleteIPNSKey()
            else:
                print "Err: The remote repo has been updated by other user, please push the repo again."
            # 删除本地的远程仓库
            os.chdir(projectLocation)
            os.system("rm -rf %s" % pathLocalRemoteRepo)
        else:
            print "ERROR: You don't have permission to push your code to the repo"
        os.system("rm %s" % remoteHash)

    elif args[0] == "transfer":
        if args[1][0:4] == "http":
            repoName = args[1].split("/")[-1]
            # accessControl = AccessControl()
            os.system("git clone --bare %s" % (args[1]))
            projectLocation = os.getcwd()
            os.chdir(repoName)
            os.system("git update-server-info")
            os.system("echo " + repr(time.time()) + " > timestamp")  # 生成一个时间戳文件

            newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
            os.popen("ipfs key gen --type=rsa --size=2048 %s" % repoName).read()
            namePublishCmd = "ipfs name publish --key=%s %s" % (repoName, newRepoHash)
            remoteHash = os.popen(namePublishCmd).read().split(" ")[2][0:-1]

            accessControl = AccessControl(remoteHash)
            accessControl.setKeyName(repoName)
            # 初始化权限管理json
            accessControl.initJson()

            newRepoHash2 = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
            namePublishCmd2 = "ipfs name publish --key=%s %s" % (repoName, newRepoHash2)
            os.system(namePublishCmd2)

            os.system("rm -rf %s/%s" % (projectLocation, repoName))
        elif len(args) == 1:
            # TODO:还需完善
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

    # elif args[0:2] == ['gen', 'userKey']:

    # 添加管理员
    elif args[0] == 'add-user':
        if len(args) == 2:
            if os.access(args[1], os.F_OK):
                projectLocation = os.getcwd()
                remoteRepo = RemoteRepo()
                remoteHash = remoteRepo.getRemoteHash()
                remoteFileHash = remoteRepo.getRemoteFileHash()
                pathLocalRemoteRepo = genKey32()
                ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteFileHash, pathLocalRemoteRepo)
                os.system(ipfsGetRepoCmd)
                os.chdir(pathLocalRemoteRepo)
                accessControl = AccessControl(remoteHash)
                accessControl.setKeyNameFromJson()
                accessControl.getUserKey("self")
                # 有权限则继续
                if accessControl.verifiAuth(accessControl.pubkey):
                    pubkey = readPublicKey(args[1])
                    accessControl.addAdmin(pubkey)

                    accessControl.savePublicKeyOfIpns(accessControl.getPublicKeyFromJson())
                    newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
                    namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash, newRepoHash)
                    os.system(namePublishCmd)
                    accessControl.deleteIPNSKey()
                else:
                    print "ERROR: You don't have permission to add admin."

                os.chdir(projectLocation)
                os.system("rm -rf %s" % pathLocalRemoteRepo)
            else:
                print "ERROR: The path doesn't exist."
        else:
            print "ERROR: Please enter a path to the public key of user."

    # 判断args[2]是否为公钥路径：
    #   不是->返回
    #   是->判断用户是否有权限：
    #       是->AccessControl.addAdmin()
    #           提交权限文件
    #       不是->返回，删除权限文件

    # 删除管理员
    elif args[0] == 'delete-user':
        if len(args) == 2:
            if os.access(args[1], os.F_OK):
                projectLocation = os.getcwd()
                remoteRepo = RemoteRepo()
                remoteHash = remoteRepo.getRemoteHash()
                remoteFileHash = remoteRepo.getRemoteFileHash()
                pathLocalRemoteRepo = genKey32()
                ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteFileHash, pathLocalRemoteRepo)
                os.system(ipfsGetRepoCmd)
                os.chdir(pathLocalRemoteRepo)
                accessControl = AccessControl(remoteHash)
                accessControl.setKeyNameFromJson()
                accessControl.getUserKey("self")
                # 有权限则继续
                if accessControl.verifiAuth(accessControl.pubkey):
                    pubkey = readPublicKey(args[1])
                    accessControl.deleteAdmin(pubkey)

                    accessControl.savePublicKeyOfIpns(accessControl.getPublicKeyFromJson())
                    newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
                    namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash, newRepoHash)
                    os.system(namePublishCmd)
                    accessControl.deleteIPNSKey()
                else:
                    print "ERROR: You don't have permission to add admin."

                os.chdir(projectLocation)
                os.system("rm -rf %s" % pathLocalRemoteRepo)
            else:
                print "ERROR: The path doesn't exist."
        else:
            print "ERROR: Please enter a path to the public key of user."
    # 判断args[2]是否为公钥路径：
    #   不是->返回
    #   是->判断用户是否有权限：
    #       是->AccessControl.deleAdmin()
    #           提交权限文件
    #       不是->返回，删除权限文件

    else:
        cmd = "git"
        for arg in args:
            cmd += " " + arg
        os.system(cmd)
    
if __name__ == '__main__':
    main()

