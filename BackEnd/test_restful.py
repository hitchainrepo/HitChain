#-*- coding: utf-8 -*-
import requests
import json

data = {"method": "getIpfsHash", "ownername": "nigel007", "reponame": "secondRepo"}

data = json.dumps(data)

response = requests.post("http://localhost:8000/webservice/", data=data)

result = response.json()
print(result)

