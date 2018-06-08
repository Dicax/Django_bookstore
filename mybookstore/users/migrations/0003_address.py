# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20180529_0704'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('is_delete', models.BooleanField(verbose_name='删除记录', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now_add=True)),
                ('receive_phone', models.CharField(verbose_name='联系方式', max_length=20)),
                ('receive_name', models.CharField(verbose_name='收货联系人', max_length=10)),
                ('receive_addr', models.CharField(verbose_name='收货地址', max_length=256)),
                ('zip_code', models.CharField(verbose_name='邮政编码', max_length=10)),
                ('is_default', models.BooleanField(verbose_name='默认地址', default=False)),
                ('passport', models.ForeignKey(verbose_name='账户', to='users.Passport')),
            ],
            options={
                'db_table': 's_user_address',
            },
        ),
    ]
