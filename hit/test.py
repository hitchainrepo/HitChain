import os


cmd = "git remote get-url --all origin"

print os.popen(cmd).read()