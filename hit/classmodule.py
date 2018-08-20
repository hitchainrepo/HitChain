class RemoteRepo():
    def __init__(self):
        import os
        print "hit get remote url"
        gitRemoteCmd = "git remote get-url --all origin"
        gitRemote = os.popen(gitRemoteCmd).read()
        gitRemoteSplit = gitRemote.split("/")
        if gitRemoteSplit[-2] == 'ipns':
            self.remoteUrl = gitRemote
            self.remoteHash = gitRemoteSplit[-1]
            print "hit resolve ipns name"
            remoteFileUrlList = os.popen("ipfs resolve /ipns/%s" % self.remoteHash).read().split("/")
            if remoteFileUrlList[1] == "ipfs":
                self.remoteFileHash = remoteFileUrlList[-1]
                print "hit get ipfs file key"
                ipfsCatTimeStamp = "ipfs cat %s/timestamp" % (self.remoteFileHash)
                self.timeStamp = os.popen(ipfsCatTimeStamp).read()

        else:
            self.remoteHash = ""
            self.timeStamp = ""
            self.remoteUrl = ""
        self.rootFileUrl = ""

    def getRemoteHash(self):
        return self.remoteHash

    def getRemoteUrl(self):
        return self.remoteUrl

    def getTimeStamp(self):
        return self.timeStamp

    def getRemoteFileHash(self):
        return self.remoteFileHash
