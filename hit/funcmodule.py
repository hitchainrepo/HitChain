# -- coding: utf-8 --
def gitPushExchange(pathLocalRemoteRepo,args):
    import os
    # TUDO:git push命令转换，将相关参数添加进命令中
    remoteNameList = os.popen("git remote").read().splitlines()
    for i,arg in enumerate(args):
        if arg in remoteNameList:
            args[i] = pathLocalRemoteRepo
        if arg[0:4] == "http":
            args[i] = pathLocalRemoteRepo
        else:
            args.insert(1,pathLocalRemoteRepo)

    pushCmd = "git"
    for arg in args:
        pushCmd += " " + arg

    return pushCmd

def genKey32():
    import random
    import string
    return ''.join(random.sample(string.ascii_letters + string.digits, 32))
