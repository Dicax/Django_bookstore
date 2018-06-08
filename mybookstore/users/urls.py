"""mybookstore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from .views import users_register, users_login, users_logout, users_info, address, order, verifycode,register_active

urlpatterns = [
    url(r'^register/$', users_register, name='register'),
    url(r'^login/$', users_login, name='login'),
    url(r'^logout/$', users_logout, name='logout'),
    url(r'^user_info$', users_info, name='user_info'),
    url(r'^address/$', address, name='address'),
    url(r'^order/(?P<page>\d+)?/?$', order, name='order'),
    url(r'^verifycode/$', verifycode, name='verifycode'),  # 验证码功能
    url(r'^active/(?P<token>.*)/$', register_active, name='active')  # 用户激活
]
