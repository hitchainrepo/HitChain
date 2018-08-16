class RemoteRepo():
    def __init__(self):
        import os
        gitRemoteCmd = "git remote get-url --all origin"
        gitRemote = os.popen(gitRemoteCmd).read()
        gitRemoteSplit = gitRemote.split("/")
        if gitRemoteSplit[-2] == 'ipfs' or gitRemoteSplit[-2] == 'ipns':
            self.remoteHash = gitRemoteSplit[-1]
            ipfsCatTimeStamp = "ipfs cat %s/timestamp" % (self.remoteUrl)
            self.timeStamp = os.popen(ipfsCatTimeStamp).read()
        else:
            self.remoteHash = ""
            self.timeStamp = ""
        self.rootFileUrl = ""

    def getHashUrlByRemote(self):
        return self.remoteHash

    def getTimeStamp(self):
        return self.timeStamp
