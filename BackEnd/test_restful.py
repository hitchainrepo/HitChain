#-*- coding: utf-8 -*-
import requests
import json

# data = {"method": "getIpfsHash", "ownername": "nigel007", "reponame": "secondRepo"}
data = {"method": "changeIpfsHash", "username": "nigel007", "password": "123456",
        "ownername": "nigel007", "reponame": "test3", "ipfsHash":"231231231231321312321"}

data = json.dumps(data)

response = requests.post("http://localhost:8000/webservice/", data=data)

result = response.json()
print(result["response"])

