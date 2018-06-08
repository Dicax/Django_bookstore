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
from django.conf.urls import url, include
from .views import detail, books_list, article
urlpatterns = [
    url(r'detail/(?P<books_id>\d+)/$', detail, name='detail'),
    url(r'list/(?P<type_id>\d+)/(?P<page>\d+)/$', books_list, name='list'),
    url(r'^comment/$', include('comments.urls', namespace='comment')),
    url(r'^article/(?P<book_id>\d+)/$', article, name='article')
]
