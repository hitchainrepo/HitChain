#-*- coding: utf-8 -*-
from suds.client import Client
import traceback

ip = "127.0.0.1"
port = "8000"
client = Client("http://%s:%s/webservice/?wsdl"%(ip, port))    #你请求的url

data = "nigel007"

try:
    result = client.service.getIpfsHash(data, "123456", "nigel007/firstRepo")
    print(result)
except:
    traceback.print_exc()