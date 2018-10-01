"""HDFS_Web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from BackEnd.views import *

urlpatterns = [
    url(r'^$', welcome, name="welcome"),
    url(r'^admin/', admin.site.urls),
    url(r'welcome/', welcome, name="welcome"),
    url(r'test/', test, name='test'),
    url(r'login/', login_view,name='login'),
    url(r'logout/', logout_view),
    url(r'register/', register_view,name='register'),
    url(r'newRepo/', newRepo, name='newRepo'),
    url(r'pushRepo/', pushRepo, name='pushRepo'),
    url(r'showAuth/', showAuth, name='showAuth'),
]
