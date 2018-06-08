from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection
import logging
from books.enums import PYTHON, JAVASCRIPT, ALGORITHMS, MACHINELEARNING, OPERATINGSYSTEM, DATABASE, BOOKS_TYPE
from books.models import Books
from comments.models import Comments

logger = logging.getLogger('django.request')


def index(request):
    """显示首页"""
    python_new = Books.objects.get_books_by_type(PYTHON, limit=3, sort='new')
    python_hot = Books.objects.get_books_by_type(PYTHON, limit=4, sort='hot')
    javascript_new = Books.objects.get_books_by_type(JAVASCRIPT, limit=3, sort='new')
    javascript_hot = Books.objects.get_books_by_type(JAVASCRIPT, limit=4, sort='hot')
    algorithms_new = Books.objects.get_books_by_type(ALGORITHMS, limit=3, sort='new')
    algorithms_hot = Books.objects.get_books_by_type(ALGORITHMS, limit=4, sort='hot')
    machinelearning_new = Books.objects.get_books_by_type(MACHINELEARNING, limit=3, sort='new')
    machinelearning_hot = Books.objects.get_books_by_type(MACHINELEARNING, limit=4, sort='hot')
    operatingsystem_new = Books.objects.get_books_by_type(OPERATINGSYSTEM, limit=3, sort='new')
    operatingsystem_hot = Books.objects.get_books_by_type(OPERATINGSYSTEM, limit=4, sort='hot')
    database_new = Books.objects.get_books_by_type(DATABASE, limit=3, sort='new')
    database_hot = Books.objects.get_books_by_type(DATABASE, limit=4, sort='hot')
    # 记录日志
    logger.info(request.session)
    # 定义模板上下文
    context = {
        'python_new': python_new,
        'python_hot': python_hot,
        'javascript_new': javascript_new,
        'javascript_hot': javascript_hot,
        'algorithms_new': algorithms_new,
        'algorithms_hot': algorithms_hot,
        'machinelearning_new': machinelearning_new,
        'machinelearning_hot': machinelearning_hot,
        'operatingsystem_new': operatingsystem_new,
        'operatingsystem_hot': operatingsystem_hot,
        'database_new': database_new,
        'database_hot': database_hot,
    }
    return render(request, 'books/index.html', context)


def detail(request, books_id):
    """显示商品的详情信息"""
    # 获取商品的详情信息
    books = Books.objects.get_books_by_id(books_id=books_id)

    if not books:
        """商品不存在,跳转到首页"""
        return redirect(reverse('index'))

    # 新品推荐
    books_li = Books.objects.get_books_by_type(type_id=books.type_id, limit=2, sort='new')

    # 用户登录之后，才记录浏览记录
    # 每个用户浏览记录对应redis中的一条信息  格式:'history_用户id':[10,9,2,3,4]
    if request.session.has_key('islogin'):
        # 用户已经登录，记录浏览记录
        con = get_redis_connection('default')
        key = 'history_%d' % request.session.get('passport_id')
        # 先从redis列表中移除books.id
        con.lrem(key, 0, books.id)
        con.lpush(key, books.id)
        # 保存用户最近浏览的5个商品
        con.ltrim(key, 0, 4)
    # 当前商品类型
    type_title = BOOKS_TYPE[books.type_id]
    # 定义上下文
    context = {'books': books, 'books_li': books_li, 'type_title': type_title}
    return render(request, 'books/detail.html', context)


def books_list(request, type_id, page):
    """商品列表页面"""
    sort = request.GET.get('sort', 'default')

    # 判断type_id是否合法
    if int(type_id) not in BOOKS_TYPE.keys():
        return redirect(reverse('books:index'))
    # 根据商品种类id和排序方法查询数据
    books_li = Books.objects.get_books_by_type(type_id=type_id, sort=sort)
    # 分页 ,每页一本
    paginator = Paginator(books_li, 1)
    # 获取一共分了多少页,总页数
    num_page = paginator.num_pages
    # 判断参数是否合理，取第page页数据
    if page == '' or int(page) > num_page:
        page = 1
    else:
        page = int(page)
    # 返回一个page类实例对象
    books_li = paginator.page(page)

    # 进行页码设置
    # 1.总页数小于5,显示所有页码
    # 2.当前页是前三页，显示1-5页
    # 3.当前页是后三页,显示后5页
    # 4.其他情况显示前两页，后两页，当前页
    # 返回的pages是一个页码列表
    if num_page < 5:
        pages = range(1, num_page + 1)
    elif page <= 3:
        pages = range(1, 6)
    elif num_page - page <= 2:
        pages = range(num_page - 4, num_page + 1)
    else:
        pages = range(page - 2, page + 3)

    # 新品推荐
    books_new = Books.objects.get_books_by_type(type_id=type_id, sort='new', limit=2)

    # 定义上下文
    type_title = BOOKS_TYPE[int(type_id)]
    context = {
        'books_li': books_li,
        'books_new': books_new,
        'type_id': type_id,
        'sort': sort,
        'type_title': type_title,
        'pages': pages
    }
    return render(request, 'books/list.html', context)


def article(request, book_id):
    """评论页面"""
    if request.method == 'GET':
        print(book_id)
        book = Books.objects.get_books_by_id(book_id)
        return render(request, 'books/article.html', {'book': book})
    elif request.method == 'POST':
        if request.session.has_key('islogin'):
            if book_id:
                content = request.POST.get('comment', '')
                title = request.POST.get('title', '')

                comment = Comments()
                comment.user_id = request.session.get('passport_id')
                comment.book_id = int(book_id)
                comment.content = content
                comment.title = title
                comment.save()

                context = {
                    'comment': comment,
                    'book_id': book_id
                }
                return redirect(reverse('books:article', book_id, context))
        else:
            return render(request, 'books/index.html')
