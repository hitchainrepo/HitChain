# -- coding: utf-8 --
import sys
import os
# import random
# import string
import time
from .classmodule import *
from .funcmodule import *
import urllib2
import json
import ConfigParser
import getpass
import requests


def main():
    args = sys.argv[1:]
    # print args
    if args[0] == 'push':
        projectLocation = os.getcwd()

        remoteRepo = RemoteRepoPlatform()
        # get remote ipns hash
        remoteUrl = remoteRepo.remoteIpfsUrl

        username = input("user name: ")
        pwd = getpass.getpass('password: ')
        if remoteRepo.verifiAuth(username,pwd):
            # gen a key to store remote repo
            pathLocalRemoteRepo = genKey32()
            # download remote repo to local
            print "hit get ipfs repo to local"
            ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteUrl,pathLocalRemoteRepo) # 要重命名
            print ipfsGetRepoCmd
            os.system(ipfsGetRepoCmd)
            # push repo to downloaded remote repo
            print "hit push to local"
            gitPushCmd = "git push %s" % (pathLocalRemoteRepo)
            for arg in args[1:]:
                # TODO:
                # if user add a remote url, there should changes it to hit command
                gitPushCmd += " " + arg
            os.system(gitPushCmd)
            # get timestamp (remoteTimeStamp) of the remote repo
            # print "compare local repo with remote repo"
            # remoteTimeStamp = os.popen("ipfs cat %s/timestamp" % remoteFileHash).read()
            # if remoteRepo.timeStamp == remoteTimeStamp:
            os.chdir(pathLocalRemoteRepo)
            # update git repo
            os.system("git update-server-info")
            # gen a timestamp file for new repo
            # os.system("echo " + repr(time.time()) + " > timestamp")
            # add new repo to ipfs network
            # use ipfs add -r .
            # print "add repo to ipfs network"
            addResponse = os.popen("ipfs add -r .").read()
            lastline = addResponse.splitlines()[-1].lower()
            if lastline != "added completely!":
                print lastline
                return
            newRepoHash = addResponse.splitlines()[-2].split(" ")[1]
            # get ipfs hash of new add repo, and publish it to ipns
            # accessControl.savePublicKeyOfIpns(accessControl.getPublicKeyFromJson())
            # print "publish file to ipns %s" % remoteHash
            # namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash,newRepoHash)
            dataUpdate = json.dumps({"method":"changeIpfsHash","username":username,"password":pwd,
                                     "reponame":remoteRepo.repoName,"ownername":remoteRepo.userName,
                                     "ipfshash":newRepoHash})
            updateRequest = requests.post(remoteRepo.repoIpfsUrl, data=dataUpdate)
            # os.system(namePublishCmd)
            # accessControl.deleteIPNSKey()
            # else:
            #     print "Err: The remote repo has been updated by other user, please push the repo again."
            # rm temp local repo
            print updateRequest
            os.chdir(projectLocation)
            os.system("rm -rf %s" % pathLocalRemoteRepo)
        else:
            print "ERROR: Access denied to push your code to the repo"

    elif args[0] == "create":
        #TODO:
        return

    elif args[0] == "transfer":
        if args[1][0:4] == "http":
            repoName = args[1].split("/")[-1]
            # accessControl = AccessControl()
            os.system("git clone --bare %s" % (args[1]))
            projectLocation = os.getcwd()
            os.chdir(repoName)
            os.system("git update-server-info")
            # os.system("echo " + repr(time.time()) + " > timestamp")  # 生成一个时间戳文件

            username = args[2]
            password = args[3]
            newRepoName = args[4]
            repoUrl = ""

            config = Config()
            config.initConfig(newRepoName,username)

            response = os.popen("ipfs add -r .").read()
            lastline = response.splitlines()[-1].lower()
            if lastline != "added completely!":
                print lastline
                return
            # newRepoHash = response.splitlines()[-1].split(" ")[1]
            newRepoHash = response.splitlines()[-2].split(" ")[1]
            # os.popen("ipfs key gen --type=rsa --size=2048 %s" % repoName).read()
            # namePublishCmd = "ipfs name publish --key=%s %s" % (repoName, newRepoHash)
            # remoteHash = os.popen(namePublishCmd).read().split(" ")[2][0:-1]

            # connect to the restful webservice
            import requests
            import json
            data = {"method": "hitTransfer", "username": username, "password": password, "reponame": newRepoName, "ipfsHash":newRepoHash}
            data = json.dumps(data)
            response = requests.post("http://localhost:8000/webservice/", data=data)
            response = response.json()
            if response["response"] != "success":
                return

            # result = response.json()
            # url = "http://localhost:8000/newRepo?username=" + username + "&password=" + password + "&reponame=" + newRepoName + "&ipfsHash=" + newRepoHash
            # req = urllib2.Request(url)
            # res_data = urllib2.urlopen(req)
            # res = res_data.read().decode('utf-8')
            # res = json.loads(res)
            # if res["response"] != "success":
            #     return

            # accessControl = AccessControl(remoteHash)
            # accessControl.setKeyName(repoName)
            # # initial authority file
            # accessControl.initJson()
            #
            # newRepoHash2 = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
            # namePublishCmd2 = "ipfs name publish --key=%s %s" % (repoName, newRepoHash2)
            # os.system(namePublishCmd2)
            #
            # os.system("rm -rf %s/%s" % (projectLocation, repoName))
        elif len(args) == 1:
            # TODO:
            # this method is not finish
            # we use this to upload a local repo to ipfs netwrok
            repoName = args[1].split("/")[-1]
            # change local repo to a bare repo
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

    # add user to authority file
    # use the public key of user
    # elif args[0] == 'add-user':
    #     if len(args) == 2:
    #         if os.access(args[1], os.F_OK):
    #             projectLocation = os.getcwd()
    #             remoteRepo = RemoteRepo()
    #             remoteHash = remoteRepo.getRemoteHash()
    #             remoteFileHash = remoteRepo.getRemoteFileHash()
    #             pathLocalRemoteRepo = genKey32()
    #             ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteFileHash, pathLocalRemoteRepo)
    #             os.system(ipfsGetRepoCmd)
    #             os.chdir(pathLocalRemoteRepo)
    #             accessControl = AccessControl(remoteHash)
    #             accessControl.setKeyNameFromJson()
    #             accessControl.getUserKey("self")
    #             # judge authority
    #             if accessControl.verifiAuth(accessControl.pubkey):
    #                 pubkey = readPublicKey(args[1])
    #                 accessControl.addAdmin(pubkey)
    #
    #                 accessControl.savePublicKeyOfIpns(accessControl.getPublicKeyFromJson())
    #                 newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
    #                 namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash, newRepoHash)
    #                 os.system(namePublishCmd)
    #                 accessControl.deleteIPNSKey()
    #             else:
    #                 print "ERROR: You don't have permission to add admin."
    #
    #             os.chdir(projectLocation)
    #             os.system("rm -rf %s" % pathLocalRemoteRepo)
    #             # os.system("rm %s" % )
    #         else:
    #             print "ERROR: The path doesn't exist."
    #     else:
    #         print "ERROR: Please enter a path to the public key of user."

    # the process of add user
    # 判断args[2]是否为公钥路径：
    #   不是->返回
    #   是->判断用户是否有权限：
    #       是->AccessControl.addAdmin()
    #           提交权限文件
    #       不是->返回，删除权限文件

    # delete user from authority file
    # through public key to identify user
    # elif args[0] == 'delete-user':
    #     if len(args) == 2:
    #         if os.access(args[1], os.F_OK):
    #             projectLocation = os.getcwd()
    #             remoteRepo = RemoteRepo()
    #             remoteHash = remoteRepo.getRemoteHash()
    #             remoteFileHash = remoteRepo.getRemoteFileHash()
    #             pathLocalRemoteRepo = genKey32()
    #             ipfsGetRepoCmd = "ipfs get %s -o %s" % (remoteFileHash, pathLocalRemoteRepo)
    #             os.system(ipfsGetRepoCmd)
    #             os.chdir(pathLocalRemoteRepo)
    #             accessControl = AccessControl(remoteHash)
    #             accessControl.setKeyNameFromJson()
    #             accessControl.getUserKey("self")
    #             # judge authority
    #             if accessControl.verifiAuth(accessControl.pubkey):
    #                 pubkey = readPublicKey(args[1])
    #                 accessControl.deleteAdmin(pubkey)
    #
    #                 accessControl.savePublicKeyOfIpns(accessControl.getPublicKeyFromJson())
    #                 newRepoHash = os.popen("ipfs add -r .").read().splitlines()[-1].split(" ")[1]
    #                 namePublishCmd = "ipfs name publish --key=%s %s" % (remoteHash, newRepoHash)
    #                 os.system(namePublishCmd)
    #                 accessControl.deleteIPNSKey()
    #             else:
    #                 print "ERROR: You don't have permission to add admin."
    #
    #             os.chdir(projectLocation)
    #             os.system("rm -rf %s" % pathLocalRemoteRepo)
    #         else:
    #             print "ERROR: The path doesn't exist."
    #     else:
    #         print "ERROR: Please enter a path to the public key of user."

    # the process of delete user
    # 判断args[2]是否为公钥路径：
    #   不是->返回
    #   是->判断用户是否有权限：
    #       是->AccessControl.deleAdmin()
    #           提交权限文件
    #       不是->返回，删除权限文件

    else:
        cf = ConfigParser.ConfigParser()
        cf.read(".git/config")
        cf.set("remote \"origin\"","url",RemoteRepoPlatform().remoteIpfs)
        cmd = "git"
        for arg in args:
            cmd += " " + arg
        os.system(cmd)
    
if __name__ == '__main__':
    main()

