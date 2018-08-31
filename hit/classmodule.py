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
    def __init__(self,pathhash):
        self.filePath = "~/.hit/"
        from .funcmodule import mkdir
        mkdir(self.filePath)
        self.ipfsKeyPath = "~/.ipfs/keystore"
        self.pathhash = pathhash

    def setKeyName(self,keyName):
        self.keyName = keyName

    def initKeyNameFromJson(self):
        import json
        with open(self.keyName, 'r', encoding='utf-8') as f:
            jsonDict = json.load(f)
            f.close()
        self.keyName = jsonDict["keyName"]

    def initJson(self):
        import json
        self.createUserKey("self")
        publicKeyIpns = self.getPublicKeyOfIPNS()
        jsonDict = {"keyName":self.keyName,
                "auth":[{'userKey':self.pubkey.save_pkcs1().decode(),
                         "publicKey":self.encrypt(publicKeyIpns,self.pubkey)}]}
        with open(self.pathhash, 'w', encoding='utf-8') as fout:
            fout.writelines(json.dumps(jsonDict))
            fout.close()

    def getPublicKeyOfIPNS(self):
        import binascii
        f = open(self.ipfsKeyPath+self.keyName, "rb+")
        data = f.read()
        f.close()
        return binascii.b2a_hex(data)

    def createUserKey(self,userKeyName):
        import os
        if os.access(self.filePath+userKeyName+'.public.pem',os.F_OK) and os.access(self.filePath+userKeyName+'.private.pem',os.F_OK):
            print "The key already exists"
        else:
            import rsa
            (self.pubkey, self.privkey) = rsa.newkeys(1024)

            with open(self.filePath+userKeyName+'.public.pem', 'w+') as f:
                f.write(self.pubkey.save_pkcs1().decode())
                f.close()
            with open(self.filePath+userKeyName+'.private.pem', 'w+') as f:
                f.write(self.privkey.save_pkcs1().decode())
                f.close()

    def getUserKey(self,userKeyName):
        import rsa
        filePath = "~/.hit/"
        with open(filePath+userKeyName+'public.pem', 'r') as f:
            self.pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
            f.close()
        with open(filePath+userKeyName+'private.pem', 'r') as f:
            self.privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())
            f.close()

    @staticmethod
    def encrypt(message,pubkey):
        import rsa
        return rsa.encrypt(message.encode(), pubkey)

    @staticmethod
    def decrypt(crypto,privkey):
        import rsa
        return rsa.decrypt(crypto, privkey).decode()

    @staticmethod
    def sign(message,privkey):
        import rsa
        return rsa.sign(message.encode(), privkey, 'SHA-1')

    @staticmethod
    def verify(message,signature,pubkey):
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
            if self.verifiAuth(userPublicKey):
                print "The user is already in the list."
            else:
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
            if self.verifiAuth(userPublicKey):
                jsonDict["auth"].remove({'userKey': userPublicKey.save_pkcs1().decode(),
                                         "publicKey": self.encrypt(publicKeyIpns, userPublicKey)})
                with open(self.keyName, 'w', encoding='utf-8') as fout:
                    fout.writelines(json.dumps(jsonDict))
                    fout.close()
                print "The user have been deleted."
            else:
                print "The user is not in the list."
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
                break
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
                break
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

    def deleteUserKey(self,userKeyName):
        import os
        os.syste("rm "+ self.filePath + userKeyName + '.public.pem')
        os.syste("rm "+ self.filePath + userKeyName + '.private.pem')

