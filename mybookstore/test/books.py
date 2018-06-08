import json

from django.shortcuts import render
from django_redis import get_redis_connection

from books.enums import PYTHON
from books.models import Books


def index(request):
    conn = get_redis_connection('default')
    python_hot_redis = conn.get('index')
    if python_hot_redis:
        python_hot_redis = json.loads(python_hot_redis)
        print('命中缓存')
        return render(request, 'books/index.html', {
            'python_hot': python_hot_redis
        })

    python_hot = Books.objects.get_books_by_type(PYTHON, limit=4, sort='hot')
    print("命中数据库")

    python_hot_redis = []
    for book in python_hot:
        python_hot_redis.append({
            'name': book.name,
            'price': str(book.price)
        })

    conn.setex('index', 60, json.dumps(python_hot_redis))


    context = {
        'python_hot': python_hot
    }

    return render(request, 'books/index.html', context)