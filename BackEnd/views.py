# -*- coding: utf-8 -*-
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from BackEnd.models import *
from BackEnd.utils import *

import json
import re

from django.http import HttpResponseNotAllowed
from rest_framework.parsers import JSONParser
from rest_framework import status

# from django.shortcuts import render,HttpResponse
# from spyne import Application,rpc,ServiceBase,Iterable,Integer,Unicode
# from spyne.protocol.soap import Soap11
# from spyne.server.wsgi import WsgiApplication
# from spyne import Iterable
# from spyne.protocol.xml import XmlDocument
# from spyne.server.django import DjangoApplication
# from django.views.decorators.csrf import csrf_exempt
# from xml.etree import ElementTree



def welcome(request):
    username = request.user.username
    if username:
        repos = Repo.objects.filter(username=username)
    else:
        repos = []
    return render(request, "welcome.html", locals())

def test(request):
    api_id = request.GET.get('api_id', None)
    return render(request, 'test.html', locals())

@csrf_exempt
def register_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        # judge whether enter username
        if username is None or username == "" or password is None or password == "":
            context['empty'] = True
            return render(request, 'register.html', context)

        if len(username) > 39:
            context['long'] = True
            return render(request, 'register.html', context)

        # judge whether there exists special characters
        specialToken = re.findall(r'[^a-zA-Z0-9\-]', username)
        if len(specialToken) > 0:
            context['specialToken'] = True
            return render(request, 'register.html', context)
        if username.startswith("-") or username.endswith("-"):
            context['specialToken'] = True
            return render(request, 'register.html', context)

        # judge whether the user exists
        user = User.objects.filter(username=username)
        # user = auth.authenticate(username = username,password = password)
        if user:
            context['userExist']=True
            return render(request, 'register.html', context)


        #添加到数据库（还可以加一些字段的处理）
        user = User.objects.create_user(username=username, password=password)
        user.save()

        #添加到session
        request.session['username'] = username
        #调用auth登录
        auth.login(request, user)
        #重定向到首页
        return redirect('/')
    else:
        context = {'isLogin':False}
    #将req 、页面 、以及context{}（要传入html文件中的内容包含在字典里）返回
    return render(request, 'register.html', context)

#登陆
@csrf_exempt
def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        #获取的表单数据与数据库进行比较
        user = authenticate(username = username,password = password)
        if user:
            #比较成功，跳转index
            auth.login(request, user)
            request.session['username'] = username
            return redirect("/")
        else:
            #比较失败，还在login
            context = {'isLogin': False, 'password':False}
            return render(request, 'login.html', context)
    else:
        context = {'isLogin': False, 'password':True}
    return render(request, 'login.html', context)

#登出
def logout_view(request):
    #清理cookie里保存username
    auth.logout(request)
    return redirect('/')


@csrf_exempt
def newRepo(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username')
        reponame = request.POST.get('reponame')

        repoInfo = {"reponame":reponame}
        userInfo = {"username":username}


        # judge whether enter username and reponame
        if reponame is None or reponame == "":
            context['empty'] = True
            return render(request, 'new.html', context)

        if len(reponame) > 39:
            context['long'] = True
            return render(request, 'new.html', context)

        # judge whether there exists special characters
        specialToken = re.findall(r'[^a-zA-Z0-9\-]', reponame)
        if len(specialToken) > 0:
            context['specialToken'] = True
            return render(request, 'new.html', context)


        # judge whether the repo already existed
        repoAlready = Repo.objects.filter(username=username, reponame=reponame)
        if repoAlready:
            context["repoExist"] = True
            return render(request, 'new.html', context)

        newIpfsHash = createIpfsRepository(repoInfo, userInfo)
        if newIpfsHash == None:
            # return JsonResponse(data={"result": "new repository error"}, status=status.HTTP_400_BAD_REQUEST)
            context["newRepoError"] = True
            return render(request, "new.html", context)

        repoItem = Repo()
        repoItem.username = username
        repoItem.reponame = reponame
        # repoItem.ipfs_hash = "QmdfYLM2jQRF6EMWNQwbMeTmqrxw1YAFA4ithj6KctVRZ8" # the hash value of README file
        repoItem.ipfs_hash = newIpfsHash
        currentTime = getCurrentTime()
        repoItem.create_time = currentTime
        repoItem.save()

        authItem = Authority()
        authItem.username = username
        authItem.repo_id = repoItem.id
        authItem.create_time = currentTime
        authItem.user_type = "owner"
        Authority.save(authItem)

        return redirect("/")

    if request.method == 'GET':
        if request.user.is_authenticated():
            return render(request, 'new.html')
        else:
            redirect("/")


def pushRepo(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        reponame = request.POST.get('reponame')
        ipfsHash = request.POST.get('ipfsHash')
        print("username="+username)
        print("password="+password)
        print("reponame="+reponame)
        print("ipfsHash="+ipfsHash)


def showAuth(request):
    repoId = request.GET.get('repoId')
    auths = Authority.objects.filter(repo_id=repoId)
    coreDevs = []
    ownerDev = None
    for auth in auths:
        coreDevs.append(auth.username)
        if auth.user_type == "owner":
            ownerDev = auth.username
    return render(request, "authority.html", locals())

def addAuth(request):
    if request.method == 'POST':
        context = {}
        username = request.POST.get('username')
        repoId = request.POST.get('repoId')

        # judge whether username right
        userExist = User.objects.filter(username=username)
        if userExist:

            # judge whether user already core developers or owner
            authorityExist = Authority.objects.filter(username=username, repo_id=repoId)
            if authorityExist:
                context["authorityExist"] = True
                return render(request, "addAuth.html", locals())

            authItem = Authority()
            authItem.username = username
            authItem.repo_id = repoId
            authItem.create_time = getCurrentTime()
            authItem.user_type = "core"
            Authority.save(authItem)

            return redirect("/showAuth?repoId=" + repoId)
        else:
            # user does not exist
            context["userExist"] = False
            return render(request, "addAuth.html", locals())

    else:
        repoId = request.GET.get("repoId")
    return render(request, 'addAuth.html', locals())

def removeAuth(request):
    repoId = request.GET.get("repoId")
    username = request.GET.get("username")
    owner = request.user.username
    ownerItem = Authority.objects.filter(repo_id=repoId, username=owner)
    if ownerItem and ownerItem[0].user_type == "owner":
        Authority.objects.filter(repo_id=repoId, username=username).delete()
    return redirect('/showAuth?repoId=' + repoId)




def searchUsername(request):
    query = request.GET['q']
    items = User.objects.filter(username__contains=query)
    result = []
    for item in items:
        result.append(item.username)
    return HttpResponse(json.dumps(result), content_type='application/json')


# add by Nigel start: RESTful API
@csrf_exempt
def webservice(request):
    responseList = {
        "user": "username or password error",
        "repo": "wrong repository",
        "auth": "no authority",
        "success": "success",
        "json": "data not in json format",
        "request": "bad request",
        "get": "do not support get request",
        "exist": "repo already exists",
    }
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            if "method" not in data:
                content = {"response": responseList["request"]}
                return JsonResponse(data=content, status=status.HTTP_200_OK)
            else:
                method = data["method"]
                if method == "getIpfsHash":
                    if "ownername" not in data or "reponame" not in data:
                        content = {"response": responseList["request"]}
                        return JsonResponse(data=content, status=status.HTTP_200_OK)
                    else:
                        ownername = data["ownername"]
                        reponame = data["reponame"]
                        ownerItem = Repo.objects.filter(username=ownername, reponame=reponame)
                        if len(ownerItem) <= 0:
                            content = {"response":responseList["repo"]}
                            return JsonResponse(data=content, status=status.HTTP_200_OK)
                        else:
                            ownerItem = ownerItem[0]
                            content = {"response":responseList["success"], "ipfs_hash":ownerItem.ipfs_hash}
                            return JsonResponse(data=content, status=status.HTTP_200_OK)
                elif method == "changeIpfsHash":
                    if "username" not in data or "password" not in data or "ownername" not in data or "reponame" not in data or "ipfsHash" not in data:
                        content = {"response": responseList["request"]}
                        return JsonResponse(data=content, status=status.HTTP_200_OK)
                    else:
                        username = data["username"]
                        password = data["password"]
                        ownername = data["ownername"]
                        reponame = data["reponame"]
                        newIpfsHash = data["ipfsHash"]

                        user = auth.authenticate(username=username, password=password)
                        if not user:
                            content = {"response":responseList["user"]}
                            return JsonResponse(data=content, status=status.HTTP_200_OK)

                        ownerItem = Repo.objects.filter(username=ownername, reponame=reponame)
                        if len(ownerItem) <= 0:
                            content = {"response":responseList["repo"]}
                            return JsonResponse(data=content, status=status.HTTP_200_OK)
                        else:
                            ownerItem = ownerItem[0]
                            repoId = ownerItem.id
                            authorityItem = Authority.objects.filter(repo_id=repoId, username=username)
                            if authorityItem:
                                ownerItem.ipfs_hash = newIpfsHash
                                ownerItem.save()
                                content = {"response":responseList["success"]}
                                return JsonResponse(data=content, status=status.HTTP_200_OK)
                            else:
                                content = {"response":responseList["auth"]}
                                return JsonResponse(data=content, status=status.HTTP_200_OK)

                elif method == "hitTransfer":
                    if "username" not in data or "password" not in data or "reponame" not in data or "ipfsHash" not in data:
                        content = {"response": responseList["request"]}
                        return JsonResponse(data=content, status=status.HTTP_200_OK)
                    else:
                        username = data["username"]
                        password = data["password"]
                        reponame = data["reponame"]
                        ipfsHash = data["ipfsHash"]

                        # judge whether the username and password right
                        user = auth.authenticate(username=username, password=password)
                        if user:
                            # judge whether the reponame of this user exists
                            repos = Repo.objects.filter(username=username, reponame=reponame)
                            if len(repos) == 0:
                                newRepo = Repo()
                                newRepo.username = username
                                newRepo.reponame = reponame
                                newRepo.ipfs_hash = ipfsHash
                                currentTime = getCurrentTime()
                                newRepo.create_time = currentTime
                                newRepo.save()

                                newAuth = Authority()
                                newAuth.username = username
                                newAuth.repo_id = newRepo.id
                                newAuth.create_time = currentTime
                                newAuth.user_type = "owner"
                                newAuth.save()

                                content = {"response":responseList["success"]}
                                return JsonResponse(data=content, status=status.HTTP_200_OK)
                            else:
                                content = {"response":responseList["exist"]}
                                return JsonResponse(data=content, status=status.HTTP_200_OK)
                        else:
                            content = {"response":responseList["user"]}
                            return JsonResponse(data=content, status=status.HTTP_200_OK)
                else:
                    content = {"response":responseList["request"]}
                    return JsonResponse(data=content, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            content = {"response": responseList["json"]}
            return JsonResponse(data=content, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    elif request.method == 'GET':
        content = {'response': responseList["get"]}
        return JsonResponse(data=content, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    return HttpResponseNotAllowed(permitted_methods=['POST'])
# add by Nigel end


# # add by Nigel start: webservice
# class HDFS(ServiceBase):
#     @rpc(Unicode, Unicode, Unicode, _returns=Iterable(Unicode))
#     def changeIpfsHash(ctx, username, password, repo):
#
#         responseList = {
#             "user": "username or password error",
#             "repo": "wrong repository",
#             "auth": "no authority",
#             "success": "success"
#         }
#
#         user = auth.authenticate(username=username, password=password)
#         dic = {"response":"user"}
#         if user:
#             if repo is None:
#                 dic = {"response":responseList["repo"]}
#             else:
#                 index_left = repo.find("/")
#                 if index_left < 0:
#                     dic = {"response":responseList["repo"]}
#                 else:
#                     ownername = repo[:index_left]
#                     reponame = repo[index_left + 1:]
#                     ownerItem = Repo.objects.filter(username=ownername, reponame=reponame)
#                     if len(ownerItem) <= 0:
#                         dic = {"response":responseList["repo"]}
#                     else:
#                         ownerItem = ownerItem[0]
#                         repoId = ownerItem.id
#                         authorityItem = Authority.objects.filter(repo_id=repoId, username=username)
#                         if authorityItem:
#                             dic = {"response":responseList["success"], "ipfs_hash":ownerItem.ipfs_hash}
#                         else:
#                             dic = {"response":responseList["auth"]}
#         return HttpResponse(json.dumps(dic))
#
#     @rpc(Unicode, _returns=Iterable(Unicode))
#     def getIpfsHash(ctx, repo):
#         responseList = {
#             "repo": "wrong repository",
#             "success": "success"
#         }
#         dic = {"response":responseList["repo"]}
#         if repo is None:
#             dic = {"response":responseList["repo"]}
#         else:
#             index_left = repo.find("/")
#             if index_left < 0:
#                 dic = {"response":responseList["repo"]}
#             else:
#                 ownername = repo[:index_left]
#                 reponame = repo[index_left + 1:]
#                 ownerItem = Repo.objects.filter(username=ownername, reponame=reponame)
#                 if len(ownerItem) <= 0:
#                     dic = {"response":responseList["repo"]}
#                 else:
#                     ownerItem = ownerItem[0]
#                     dic = {"response":responseList["success"], "ipfs_hash":ownerItem.ipfs_hash}
#         return HttpResponse(json.dumps(dic))
#
# application = Application([HDFS],
#     tns='spyne.examples.hello',
#     in_protocol=Soap11(validator='lxml'),
#     out_protocol=Soap11()
# )
#
# webservice = csrf_exempt(DjangoApplication(application))
# # add by Nigel end: webservice