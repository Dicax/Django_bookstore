from datetime import datetime
from django.db import transaction
from django.http import JsonResponse
from django_redis import get_redis_connection

from books.models import Books
from order.models import OrderInfo, OrderGoods
from users.models import Address


def order_commit(request):
    """生成订单"""
    if not request.session.has_key('islogin'):
        return JsonResponse({'res': 1, 'msg': '用户未登录'})
    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    books_ids = request.POST.get('books_ids')

    if not all([addr_id, pay_method, books_ids]):
        return JsonResponse({'res': 2, 'msg': '数据不完整'})

    if int(pay_method) not in OrderInfo.PAY_METHODS_ENUM.values():
        return JsonResponse({'res': 3, 'msg': '不存在付款方式'})

    add = Address.objects.filter(addr_id=addr_id)
    if len(add) == 0:
        return JsonResponse({'res': 4, 'msg': '地址信息有错'})

    # 订单创建
    # 组织订单信息
    passport_id = request.session.get('passport_id')

    order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(passport_id)

    transport_price = 10
    total_count = 0
    total_price = 0
    # 创建一个保存点
    sid = transaction.savepoint()

    try:
        order = OrderInfo.objects.create(
            order_id=order_id,
            passport_id=passport_id,
            addr_id=addr_id,
            total_count=total_count,
            total_price=total_price,
            transport_price=transport_price,
            pay_method=pay_method
        )
        books_ids = books_ids.split(',')
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % passport_id

        for id in books_ids:
            book = Books.objects.get_books_by_id(passport_id=id)
            if not book:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res': 4, 'errmsg': '商品信息错误'})
            count = conn.hget(cart_key, id)
            if int(count) > book.stock:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res': 5, 'errmsg': '库存不足'})
            OrderGoods.objects.create(
                order_id=order_id,
                count=count,
                price=book.price,
                books_id=id
            )
            book.sales += count
            book.stock -= count
            book.save()

            total_count += int(count)
            total_price += book.price * int(count)
            order.save()

        order.total_count = total_count
        order.total_price = total_price

    except Exception as e:
        # 数据库出错,回滚
        transaction.savepoint_rollback(sid)
        return JsonResponse({'res': 7, 'errmsg': '服务器错误'})
    conn.hdel(cart_key, *books_ids)
    transaction.savepoint_commit(sid)
    return JsonResponse({'res': 6})
