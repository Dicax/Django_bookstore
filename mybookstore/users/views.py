from django_redis import get_redis_connection

from books.models import Books
from users.tasks import send_active_email
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from mybookstore import settings
from order.models import OrderInfo, OrderGoods
from users.models import Passport, Address
from utils.utils import login_required
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.http import HttpResponse
import os
import re


# from itsdangerous import SignatureExpired


def verifycode(request):
    # 引入绘图模块
    from PIL import Image, ImageDraw, ImageFont
    import random

    # 定义变量,用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point函数绘制燥点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象
    font = ImageFont.truetype(os.path.join(settings.BASE_DIR, "Ubuntu-RI.ttf"), 15)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    # 存入session,用于做一步验证
    request.session['verifycode'] = rand_str
    # 内存文件操作
    import io
    buf = io.BytesIO()
    # 将图片保存到内存中,文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端,MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


def users_register(request):
    """用户注册页面"""
    if request.method == 'GET':
        return render(request, 'users/register.html')
    elif request.method == 'POST':
        """进行用户注册处理"""
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        if not all([username, password, email]):
            # 数据校验
            return render(request, 'users/register.html', {'errmsg': '参数不能为空！'})

        if not re.match(r'[\w+]*@[\w+]', email):
            # email校验
            return render(request, 'users/register.html', {'errmsg': '邮箱格式不对！'})

        p = Passport.objects.check_passport(username=username)

        if p:
            return render(request, 'users/register.html', {'errmsg': '用户名已存在！'})
        passport = Passport.objects.add_one_passport(username=username, password=password, email=email)

        #  生成激活的token itsdangerous
        serializer = Serializer(settings.SECRET_KEY, 3600)
        token = serializer.dumps({'confirm': passport.id})  # 返回bytes
        token = token.decode()

        # 给用户的邮箱发送激活邮件
        # send_mail('尚硅谷书城用户激活', '', settings.EMAIL_FROM, [email], html_message='<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)
        send_active_email.delay(token, username, email)
        return redirect(reverse('user:login'))


def register_active(request, token):
    """用户账户激活"""
    serializer = Serializer(settings.SECRET_KEY, 3600)
    try:
        info = serializer.loads(token)
        passport_id = info['confirm']
        # 用户激活
        passport = Passport.objects.get(id=passport_id)
        passport.is_active = True
        passport.save()
        # 跳转到登录页
        return redirect(reverse('user:login'))
    except SignatureExpired:
        # 链接过期
        return HttpResponse('激活链接已经过期')


def users_login(request):
    if request.method == 'GET':
        """显示登录页面"""
        if request.COOKIES.get('username'):
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        context = {
            'username': username,
            'checked': checked,

        }
        return render(request, 'users/login.html', context)
    elif request.method == 'POST':
        """用户登录信息校验"""
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        verifycode = request.POST.get('verifycode')

        # 数据校验
        if not all([username, password, remember, verifycode]):
            # 数据不完整
            return JsonResponse({'res': 2})
        if verifycode.upper() != request.session['verifycode']:
            return JsonResponse({'res': 2})

        # 根据用户名和密码去匹配账户
        passport = Passport.objects.get_one_passport(username=username, password=password)

        if passport:
            next_url = reverse('index')
            jres = JsonResponse({'res': 1, 'next_url': next_url})

            if remember == 'true':
                # 记住用户名
                jres.set_cookie('username', username, max_age=7 * 24 * 3600)
            else:
                jres.delete_cookie('username')

            # 保存用户的登录状态
            request.session['islogin'] = True
            request.session['username'] = username
            # 登录成功后给passport_id赋值
            request.session['passport_id'] = passport.id
            return jres
        else:
            # 用户名或密码错误
            return JsonResponse({'res': 0})


def users_logout(request):
    # 清空用户session信息
    request.session.flush()
    # 跳转到首页
    return redirect(reverse('index'))


@login_required
def users_info(request):
    """用户中心---个人信息页"""
    # 登录成功后session保存passport_id值
    passport_id = request.session.get('passport_id')
    # 通过passport_id获取用户基本信息
    addr = Address.objects.get_default_address(passport_id=passport_id)
    # 获取用户最近浏览信息
    con = get_redis_connection('default')
    key = 'history_%d' % passport_id
    # 取出用户最近浏览的5个商品的id
    history_li = con.lrange(key, 0, 4)
    books_li = []
    for id in history_li:
        books = Books.objects.get_books_by_id(books_id=id)
        books_li.append(books)
    context = {
        'addr': addr,
        'page': 'user',
        'books_li': books_li
    }
    return render(request, 'users/user_center_info.html', context)


@login_required
def address(request):
    """用户中心--地址页"""
    # 获取用户的id
    passport_id = request.session.get('passport_id')

    if request.method == 'GET':
        # 显示地址页面
        # 查询用户的默认地址
        addr = Address.objects.get_default_address(passport_id=passport_id)
        addr_other = Address.objects.get_other_address(passport_id=passport_id)
        return render(request, 'users/user_center_site.html',
                      {'addr': addr, 'addr_other': addr_other, 'page': 'address'})
    else:
        # 添加收货地址
        # 接受数据
        receive_name = request.POST.get('username')
        receive_addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        receive_phone = request.POST.get('phone')

        # 进行校验
        if not all([receive_phone, receive_addr, receive_name, zip_code]):
            return render(request, 'users/user_center_site.html', {'errmsg': '数据不能为空'})

        # 添加收货地址
        Address.objects.add_one_address(
            passport_id=passport_id,
            receive_name=receive_name,
            receive_addr=receive_addr,
            receive_phone=receive_phone,
            zip_code=zip_code
        )

        return redirect(reverse('user:address'))


@login_required
def order(request, page):
    """用户中心--订单页"""
    passport_id = request.session.get('passport_id')
    # 获取订单信息
    order_li = OrderInfo.objects.filter(passport_id=passport_id)
    # 遍历获取订单的商品信息
    for order in order_li:
        # 根据订单id查询订单商品信息
        order_id = order.order_id
        order_books_li = OrderGoods.objects.filter(order_id=order_id)
        print('order.status========', order.status)
        # 计算商品的小计
        for order_books in order_books_li:
            count = order_books.count
            price = order_books.price
            amount = count * price
            # 保存订单中每一个商品的小计
            order_books.amount = amount

        # 给order对象增加一个属性order_books_li,保存订单中商品的信息
        order.order_books_li = order_books_li

    # 分页  每页显示三个
    paginator = Paginator(order_li, 3)
    num_pages = paginator.num_pages

    if not page:
        page = 1
    if page == '' or int(page) > num_pages:
        page = 1
    else:
        page = int(page)

    order_li = paginator.page(page)

    if num_pages < 5:
        pages = range(1, num_pages + 1)
    elif page <= 3:
        pages = range(1, 6)
    elif num_pages - page <= 3:
        pages = range(num_pages - 4, num_pages + 1)
    else:
        pages = range(page - 2, page + 3)

    context = {
        'pages': pages,
        'order_li': order_li,
    }
    return render(request, 'users/user_center_order.html', context)
