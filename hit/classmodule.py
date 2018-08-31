# -- coding: utf-8 --
class RemoteRepo():
    def __init__(self):
        import os
        print "hit get remote url"
        gitRemoteCmd = "git remote get-url --all origin"
        gitRemote = os.popen(gitRemoteCmd).read().strip('\n')
        gitRemoteSplit = gitRemote.split("/")
        if gitRemoteSplit[-2] == 'ipns':
            self.remoteUrl = gitRemote
            self.remoteHash = gitRemoteSplit[-1]
            print gitRemoteSplit
            print "hit resolve ipns name"
            remoteFileUrlList = os.popen("ipfs resolve /ipns/%s" % self.remoteHash).read().strip("\n").split("/")
            if remoteFileUrlList[1] == "ipfs":
                self.remoteFileHash = remoteFileUrlList[-1]
                print "hit get ipfs file key"
                ipfsCatTimeStamp = "ipfs cat %s/timestamp" % (self.remoteFileHash)
                print ipfsCatTimeStamp
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

class AccessControl():
    def __init__(self, keyName):
        self.keyName = keyName

    def initJson(self):
        import json
        self.createUserKey("self")
        publicKeyIpns = self.getPublicKeyOfIPNS()
        jsonDict = {"keyName":self.keyName,
                "auth":[{'userKey':self.pubkey.save_pkcs1().decode(),
                         "publicKey":self.encrypt(publicKeyIpns,self.pubkey)}]}
        with open(self.keyName, 'w', encoding='utf-8') as fout:
            fout.writelines(json.dumps(jsonDict))
            fout.close()


    def getPublicKeyOfIPNS(self):
        import binascii
        filePath = self.keyName
        f = open(filePath, "rb+")
        data = f.read()
        f.close()
        return binascii.b2a_hex(data)

    def createUserKey(self,userKeyName):
        import rsa
        (self.pubkey, self.privkey) = rsa.newkeys(1024)
        with open(userKeyName+'.public.pem', 'w+') as f:
            f.write(self.pubkey.save_pkcs1().decode())
            f.close()
        with open(userKeyName+'.private.pem', 'w+') as f:
            f.write(self.privkey.save_pkcs1().decode())
            f.close()

    def getUserKey(self,userKeyName):
        import rsa
        with open(userKeyName+'public.pem', 'r') as f:
            self.pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
            f.close()
        with open(userKeyName+'private.pem', 'r') as f:
            self.privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())
            f.close()

    def encrypt(self,message,pubkey):
        import rsa
        return rsa.encrypt(message.encode(), pubkey)

    def decrypt(self,crypto,privkey):
        import rsa
        return rsa.decrypt(crypto, privkey).decode()

    def sign(self,message,privkey):
        import rsa
        return rsa.sign(message.encode(), privkey, 'SHA-1')

    def verify(self,message,signature,pubkey):
        import rsa
        return rsa.verify(message.encode(), signature, pubkey)

    def addAdmin(self,userPublicKey):
        import json
        with open(self.keyName, 'r', encoding='utf-8') as f:
            jsonDict = json.load(f)
            f.close()
        publicKeyIpns = self.getPublicKeyOfIPNS()
        authFlag = self.verifiAuth(self.pubkey)
        if authFlag:
            jsonDict["auth"].append({'userKey':userPublicKey.save_pkcs1().decode(),
                                     "publicKey":self.encrypt(publicKeyIpns,userPublicKey)})
            with open(self.keyName, 'w', encoding='utf-8') as fout:
                fout.writelines(json.dumps(jsonDict))
                fout.close()
            print "The user have been added."
        else:
            print "You don't have authority to do this!!!"


    def deleAdmin(self,userPublicKey):
        import json
        with open(self.keyName, 'r', encoding='utf-8') as f:
            jsonDict = json.load(f)
            f.close()
        publicKeyIpns = self.getPublicKeyOfIPNS()
        authFlag = self.verifiAuth(self.pubkey)
        if authFlag:
            jsonDict["auth"].remove({'userKey': userPublicKey.save_pkcs1().decode(),
                                     "publicKey": self.encrypt(publicKeyIpns, userPublicKey)})
            with open(self.keyName, 'w', encoding='utf-8') as fout:
                fout.writelines(json.dumps(jsonDict))
                fout.close()
            print "The user have been deleted."
        else:
            print "You don't have authority to do this!!!"

    def verifiAuth(self,userPublicKey):
        import json
        with open(self.keyName, 'r', encoding='utf-8') as f:
            jsonDict = json.load(f)
            f.close()
        authFlag = False
        for userAuth in jsonDict["auth"]:
            if userAuth["userKey"] == userPublicKey.save_pkcs1().decode():
                authFlag = True
        return authFlag

    def getPublicKeyFromJson(self):
        import json
        with open(self.keyName, 'r', encoding='utf-8') as f:
            jsonDict = json.load(f)
            f.close()
        authFlag = False
        for userAuth in jsonDict["auth"]:
            if userAuth["userKey"] == self.pubkey.save_pkcs1().decode():
                publicKeyOfIPNS = self.decrypt(userAuth["publicKey"],self.privkey)
                authFlag = True
        if authFlag:
            import binascii
            dataTurn = binascii.a2b_hex(publicKeyOfIPNS)
            filePath = self.keyName
            binfile = open(filePath,'wb')
            binfile.write(dataTurn)
            print "You have generate the key for publish ipns."
        else:
            print "You don't have authority to do this!!!"

        return authFlag

    def deleteIPNSKey(self):
        import os
        cmd = "ipfs key rm %s" % self.keyName
        os.system(cmd)