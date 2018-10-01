# -*- coding: utf-8 -*-
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from BackEnd.models import *
from BackEnd.utils import *


def welcome(request):
    username = request.user.username
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
        repoItem.create_time = getCurrentTime()
        Repo.save(repoItem)
        print("this is a form")
    return render(request, 'new.html')