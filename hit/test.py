import os
import random
import string

#
# cmd = "git remote get-url --all origin"
#
# print os.popen(cmd).read()

ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))

print ran_str

print os.getcwd()
pwd = os.getcwd()
print os.path.abspath(os.path.dirname(pwd)+os.path.sep+".")
print os.path.abspath(os.path.dirname(pwd)+os.path.sep+"..")

os.chdir("..")
print os.getcwd()