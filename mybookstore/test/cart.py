from django.http import JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from books.models import Books
from utils.utils import login_required


def show(request):
    passport_id = request.session.get('passport_id')
    #  获取购物车的记录
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % passport_id
    res_dict = conn.hgetall(cart_key)

    books_li = []
    total_price = 0
    total_count = 0
    for id, count in res_dict:
        books = Books.objects.get_books_by_id(passport_id=id)
        # 把数量保存到对象中
        books.count = count
        books.amount = int(count) * books.price
        books_li.append(books)

        total_price += books.amount
        total_count += int(count)
    contex = {
        'total_price': total_price,
        'total_count': total_count
    }
    return render(request, '', contex)


def cart_add(request):
    """向购物车添加数据"""
    books_id = request.session.get('books_id')
    books_count = request.session.get('books_count')

    books = Books.objects.get_books_by_id(passport_id=books_id)
    if not all([books_id, books_count]):
        return JsonResponse({'res': 1, 'msg': '数据不完整'})

    try:
        count = int(books_count)
    except Exception as e:
        return JsonResponse({'res': 2, 'msg': "数据不合法"})

    if not books:
        return JsonResponse({'res': 3, 'msg': '商品不存在'})

    # 添加商品到购物车
    # 每个用户的购物车记录用一条hash数据保存, 格式cart_id: id count
    passport_id = request.session.get('passport_id')
    cart_id = 'cart_%d' % passport_id
    conn = get_redis_connection('default')
    res = conn.hget(cart_id, passport_id)

    if res is None:
        # 用户车的购物车中没有添加该商品，则添加数据
        res = count
    else:
        res = int(res) + count

    if res > books.store:
        return JsonResponse({'res': 4, 'msg': '库存不足'})
    else:
        conn.hset(cart_id, books_id, res)
    return JsonResponse({'res': 5, 'msg': '已添加'})


def cart_update(request):
    books_id = request.session.get('books_id')
    books_count = request.session.get('books_count')

    if not all([books_id, books_count]):
        return JsonResponse({'res': 1, 'msg': '数据不完整'})

    try:
        count = int(books_count)
    except Exception as e:
        return JsonResponse({'res': 2, 'msg': "数据不合法"})

    books = Books.objects.get_books_by_id(passport_id=books_id)
    if not books:
        return JsonResponse({'res': 3, 'msg': '商品不存在'})

    # 添加商品到购物车
    # 每个用户的购物车记录用一条hash数据保存, 格式cart_id: id count
    passport_id = request.session.get('passport_id')
    cart_id = 'cart_%d' % passport_id
    conn = get_redis_connection('default')

    if count > books.store:
        return JsonResponse({'res': 4, 'msg': '库存不足'})
    else:
        conn.hset(cart_id, books_id, count)
    return JsonResponse({'res': 5, 'msg': '已添加'})
