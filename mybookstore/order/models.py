from django.db import models
from users.models import Passport, Address
from books.models import Books

# Create your models here.
from db.base_model import BaseModel


class OrderInfoManger(models.Manager):
    """订单信息模型管理系统"""
    pass


class OrderInfo(BaseModel):
    """订单信息模型类"""
    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )
    PAY_METHODS_ENUM = {
        "CASH": 1,
        "WEIXIN": 2,
        "ALIPAY": 3,
        "UNIONPAY": 4,
    }
    ORDER_STATUS_CHOICES = (
        (1, "待支付"),
        (2, "待发货"),
        (3, "待收货"),
        (4, "待评价"),
        (5, "已完成"),
    )
    order_id = models.CharField(max_length=64, primary_key=True, verbose_name='订单编号')
    passport = models.ForeignKey('users.Passport', verbose_name='下单账号')
    addr = models.ForeignKey('users.Address', verbose_name='收货地址')
    total_count = models.IntegerField(default=1, verbose_name='订单数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总价')
    transport_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费总价')
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=1, verbose_name='付费方式')
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')
    pay_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付编号')

    objects = OrderInfoManger()

    class Meta:
        db_table = 's_order_info'


class OrderGoodsManger(models.Manager):
    pass


class OrderGoods(BaseModel):
    """订单商品模型类"""
    order = models.ForeignKey('OrderInfo', verbose_name='所属订单')
    books = models.ForeignKey('books.Books', verbose_name='订单商品')
    count = models.IntegerField(default=1, verbose_name='商品数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')

    objects = OrderGoodsManger()

    class Meta:
        db_table = 's_order_books'
