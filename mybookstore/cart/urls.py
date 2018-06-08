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
from .views import cart_add, cart_count, show, cart_del, cart_update
urlpatterns = [
    url(r'^cart_add/$', cart_add, name='cart_add'),
    url(r'^cart_update/$', cart_update, name='cart_update'),
    url(r'^cart_del/$', cart_del, name='cart_del'),
    url(r'^cart_count/$', cart_count, name='cart_count'),
    url(r'^show/$', show, name='show'),
]
