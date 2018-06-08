# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
        ('users', '0003_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderGoods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_delete', models.BooleanField(verbose_name='删除记录', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now_add=True)),
                ('count', models.IntegerField(verbose_name='商品数量', default=1)),
                ('price', models.DecimalField(verbose_name='商品价格', decimal_places=2, max_digits=10)),
                ('books', models.ForeignKey(verbose_name='订单商品', to='books.Books')),
            ],
            options={
                'db_table': 's_order_books',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('is_delete', models.BooleanField(verbose_name='删除记录', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now_add=True)),
                ('order_id', models.CharField(verbose_name='订单编号', max_length=64, serialize=False, primary_key=True)),
                ('total_count', models.IntegerField(verbose_name='订单数量', default=1)),
                ('total_price', models.DecimalField(verbose_name='订单总价', decimal_places=2, max_digits=10)),
                ('transport_price', models.DecimalField(verbose_name='运费总价', decimal_places=2, max_digits=10)),
                ('pay_method', models.SmallIntegerField(verbose_name='付费方式', default=1, choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')])),
                ('status', models.SmallIntegerField(verbose_name='订单状态', default=1, choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')])),
                ('pay_id', models.CharField(unique=True, verbose_name='支付编号', blank=True, max_length=100, null=True)),
                ('addr', models.ForeignKey(verbose_name='收货地址', to='users.Address')),
                ('passport', models.ForeignKey(verbose_name='下单账号', to='users.Passport')),
            ],
            options={
                'db_table': 's_order_info',
            },
        ),
        migrations.AddField(
            model_name='ordergoods',
            name='order',
            field=models.ForeignKey(verbose_name='所属订单', to='order.OrderInfo'),
        ),
    ]
