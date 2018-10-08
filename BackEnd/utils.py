import datetime
import random
import os
import shutil
import configparser

def getCurrentTime():
    create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return create_time


def generate_random_str(randomlength=16):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def mkdir(path):
    # new folder
    import os
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)

    if not isExists:
        print(path+': create successfull')
        os.makedirs(path)
        return True
    else:
        print(path+': path already exist')
        return False


def createLocalRepository(repoInfo, userInfo):
    baseDir = "Repos"
    username = userInfo["username"]
    reponame = repoInfo["reponame"]

    dirPath = os.path.join(baseDir, username, reponame)

    if os.path.exists(dirPath):
        shutil.rmtree(dirPath)

    os.makedirs(dirPath)

    hitPath = os.path.join(dirPath, ".hit")

    mkdir(hitPath)
    configPath = os.path.join(hitPath, "config")
    cf = configparser.ConfigParser()
    cf.read(configPath)
    cf.add_section("remote \"origin\"")
    cf.set("remote \"origin\"", "repoName", reponame)
    cf.set("remote \"origin\"", "userName", username)
    with open(configPath, "w+") as f:
        cf.write(f)
    return dirPath

# return IpfsHash if added completely
# else return None
def createIpfsRepository(repoInfo, userInfo):
    repoPath = createLocalRepository(repoInfo, userInfo)
    addResponse = os.popen("ipfs add -r " + repoPath).read()
    lastline = addResponse.splitlines()[-1].lower()
    if lastline != "added completely!":
        return None
    newRepoHash = addResponse.splitlines()[-2].split(" ")[1]
    shutil.rmtree(repoPath) # after added to ipfs net, remove the local repo
    return newRepoHash