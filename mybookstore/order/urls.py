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
from .views import order_place, order_commit, order_pay, check_pay
urlpatterns = [
    url(r'^place/$', order_place, name='place'),
    url(r'^commit/$', order_commit, name='commit'),
    url(r'^pay/$', order_pay, name='order_pay'),
    url(r'^check_pay/$', check_pay, name='check_pay'),
]
