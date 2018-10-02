# -*- coding: utf-8 -*-
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from BackEnd.models import *
from BackEnd.utils import *

import json


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

        # 判断用户是否存在
        user = auth.authenticate(username = username,password = password)
        if user:
            context['userExit']=True
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
            context = {'isLogin': False,'pawd':False}
            return render(request, 'login.html', context)
    else:
        context = {'isLogin': False,'pswd':True}
    return render(request, 'login.html', context)

#登出
def logout_view(request):
    #清理cookie里保存username
    auth.logout(request)
    return redirect('/')


@csrf_exempt
def newRepo(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        reponame = request.POST.get('reponame')
        repoItem = Repo()
        repoItem.username = username
        repoItem.reponame = reponame
        repoItem.ipfs_hash = "QmdfYLM2jQRF6EMWNQwbMeTmqrxw1YAFA4ithj6KctVRZ8" # the hash value of README file
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
    return render(request, 'new.html')


def pushRepo(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        reponame = request.POST.get('reponame')
        ipfsHash = request.POST.get('ipfsHash')


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
        username = request.POST.get('username')
        repoId = request.POST.get('repoId')

        authItem = Authority()
        authItem.username = username
        authItem.repo_id = repoId
        authItem.create_time = getCurrentTime()
        authItem.user_type = "core"
        Authority.save(authItem)

        return redirect("/showAuth?repoId=" + repoId)
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