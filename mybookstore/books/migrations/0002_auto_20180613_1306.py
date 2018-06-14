# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='books',
            name='image',
            field=models.ImageField(upload_to='books', verbose_name='商品图片', storage=django.core.files.storage.FileSystemStorage(location='/root/yun/mybookstore/collect_static')),
        ),
    ]
