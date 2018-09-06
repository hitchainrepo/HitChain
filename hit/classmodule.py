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
        import os
        self.projPath = os.getcwd()+'/'
        self.systemPath = os.path.expanduser('~')+'/'
        self.filePath = self.systemPath + ".hit/"
        from funcmodule import mkdir
        mkdir(self.filePath)
        self.ipfsKeyPath = self.systemPath + ".ipfs/keystore/"
        self.pathhash = pathhash

    def setKeyName(self,keyName):
        self.keyName = keyName

    def setKeyNameFromJson(self):
        import json
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        self.keyName = jsonDict["keyName"]

    def initJson(self):
        import json
        import des
        self.createUserKey("self")
        publicKeyIpns = self.getPublicKeyOfIPNS()
        deskey = des.keyGen()
        desClass = des.DESCipher(deskey)
        jsonDict = {"keyName":self.keyName,
                "auth":[{'userKey':self.pubkey.save_pkcs1().decode(),
                         "publicKey":desClass.des_encrypt(publicKeyIpns),
                         "DESKey":self.encrypt(deskey,self.pubkey)}]}
        with open(self.pathhash, 'w') as fout:
            fout.writelines(json.dumps(jsonDict))
            fout.close()

    def getPublicKeyOfIPNS(self):
        import binascii
        with open(self.ipfsKeyPath+self.keyName, "rb+") as f:
            data = f.read()
            f.close()
            return binascii.b2a_hex(data)

    def createUserKey(self,userKeyName):
        import os
        if os.access(self.filePath+userKeyName+'.public.pem',os.F_OK) and os.access(self.filePath+userKeyName+'.private.pem',os.F_OK):
            print "The key already exists"
            self.getUserKey(userKeyName)
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
        import os
        if os.access(self.filePath+userKeyName+'.public.pem',os.F_OK) and os.access(self.filePath+userKeyName+'.private.pem',os.F_OK):
            import rsa
            with open(self.filePath+userKeyName+'.public.pem', 'r') as f:
                self.pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
                f.close()
            with open(self.filePath+userKeyName+'.private.pem', 'r') as f:
                self.privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())
                f.close()
        else:
            print "You don't have a key named %s" % userKeyName

    @staticmethod
    def encrypt(message,pubkey):
        import rsa
        import binascii
        return binascii.b2a_hex(rsa.encrypt(message.encode(), pubkey))

    @staticmethod
    def decrypt(crypto,privkey):
        import rsa
        import binascii
        return rsa.decrypt(binascii.a2b_hex(crypto), privkey).decode()

    # @staticmethod
    # def sign(message,privkey):
    #     import rsa
    #     return rsa.sign(message.encode(), privkey, 'SHA-1')
    #
    # @staticmethod
    # def verify(message,signature,pubkey):
    #     import rsa
    #     return rsa.verify(message.encode(), signature, pubkey)

    def addAdmin(self,userPublicKey):
        import json
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        # publicKeyIpns = self.getPublicKeyOfIPNS()
        authFlag = self.verifiAuth(self.pubkey)
        if authFlag:
            if self.verifiAuth(userPublicKey):
                print "The user is already in the list."
            else:
                import des
                deskey = des.keyGen()
                desClass = des.DESCipher(deskey)
                publicKeyIpns = self.getPublicKeyFromJson()
                jsonDict["auth"].append({'userKey':userPublicKey.save_pkcs1().decode(),
                                         "publicKey":desClass.des_encrypt(publicKeyIpns),
                                         "DESKey":self.encrypt(deskey,userPublicKey)})
                with open(self.pathhash, 'w') as fout:
                    fout.writelines(json.dumps(jsonDict))
                    fout.close()
                print "The user has been added."
        else:
            print "You don't have authority to do this!!!"

    def deleteAdmin(self,userPublicKey):
        import json
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        authFlag = self.verifiAuth(self.pubkey)
        if authFlag:
            if self.verifiAuth(userPublicKey):
                for auth in jsonDict['auth']:
                    if auth["userKey"] == userPublicKey.save_pkcs1().decode():
                        jsonDict["auth"].remove(auth)
                        break
                with open(self.pathhash, 'w') as fout:
                    fout.writelines(json.dumps(jsonDict))
                    fout.close()
                print "The user have been deleted."
            else:
                print "The user is not in the list."
        else:
            print "You don't have authority to do this!!!"

    def verifiAuth(self,userPublicKey):
        import json
        with open(self.pathhash, 'r') as f:
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
        # import binascii
        with open(self.pathhash, 'r') as f:
            jsonDict = json.load(f)
            f.close()
        publicKeyOfIPNS = ''

        for userAuth in jsonDict["auth"]:
            if userAuth["userKey"] == self.pubkey.save_pkcs1().decode():
                import des
                deskey = self.decrypt(userAuth["DESKey"],self.privkey)
                desClass = des.DESCipher(str(deskey))
                publicKeyOfIPNS = desClass.des_descrypt(userAuth["publicKey"])
                break
        # if authFlag:
        #     dataTurn = binascii.a2b_hex(publicKeyOfIPNS)
        #     filePath = self.keyName
        #     binfile = open(filePath,'wb')
        #     binfile.write(dataTurn)
        #     print "You have generate the key for publish ipns."
        # else:
        #     print "You don't have authority to do this!!!"

        return publicKeyOfIPNS

    def savePublicKeyOfIpns(self,ipnsKey):
        import binascii
        dataTurn = binascii.a2b_hex(ipnsKey)
        with open(self.ipfsKeyPath+self.keyName,'wb') as f:
            f.write(dataTurn)
            f.close()
            print "You have get the key for publish ipns."

    def deleteIPNSKey(self):
        import os
        cmd = "ipfs key rm %s" % self.keyName
        os.system(cmd)

    def deleteUserKey(self,userKeyName):
        import os
        os.system("rm "+ self.filePath + userKeyName + '.public.pem')
        os.system("rm "+ self.filePath + userKeyName + '.private.pem')

