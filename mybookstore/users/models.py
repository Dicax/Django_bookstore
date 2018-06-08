from django.db import models
from db.base_model import BaseModel
from hashlib import sha1


# Create your models here.

def get_hash(str):
    """取一个字符串的hash值"""
    sh = sha1()
    sh.update(str.encode('utf8'))
    return sh.hexdigest()


class PassportManager(models.Manager):
    def add_one_passport(self, username, password, email):
        """添加一个账户信息"""
        passport = self.create(username=username, password=get_hash(password), email=email)
        return passport

    def get_one_passport(self, username, password):
        """根据用户名密码查找账户信息"""
        try:
            passport = self.get(username=username, password=get_hash(password))
        except self.model.DoesNotExist:
            passport = None
        return passport

    def check_passport(self, username):
        """检查是否存在用户名"""
        try:
            passport = self.get(username=username)
        except self.model.DoesNotExist:
            passport = None
        # if passport:
        #     return True
        return passport


class Passport(BaseModel):
    """用户模型类"""
    username = models.CharField(max_length=20, verbose_name='用户名')
    password = models.CharField(max_length=40, verbose_name='用户密码')
    email = models.EmailField(verbose_name='邮箱')
    is_active = models.BooleanField(default=False, verbose_name='激活状态')

    objects = PassportManager()

    class Meta:
        db_table = 's_user_account'


class AddressManager(models.Manager):
    """地址模型管理器类"""

    def get_default_address(self, passport_id):
        """查询指定用户的默认收货地址"""
        try:
            addr = self.get(passport_id=passport_id, is_default=True)
        except self.model.DoesNotExist:
            """没有默认收货地址"""
            addr = None
        return addr

    def get_other_address(self, passport_id):
        """查询指定用户的非默认收货地址"""
        try:
            addr = self.filter(passport_id=passport_id, is_default=False)
        except self.model.DoesNotExist:
            """没有默认收货地址"""
            addr = []
        return addr

    def add_one_address(self, passport_id, receive_phone, receive_name, receive_addr, zip_code):
        """添加收货地址"""
        # 判断是否存在收货地址
        addr = self.get_default_address(passport_id=passport_id)

        if addr:
            # 地址已存在,不用再次保存
            is_default = False
        else:
            # 保存地址
            is_default = True
        # 添加一个地址
        addr = self.create(passport_id=passport_id,
                           receive_name=receive_name,
                           receive_addr=receive_addr,
                           receive_phone=receive_phone,
                           zip_code=zip_code,
                           is_default=is_default)
        return addr


class Address(BaseModel):
    """用户收货地址模型类"""
    receive_phone = models.CharField(max_length=20, verbose_name='联系方式')
    receive_name = models.CharField(max_length=10, verbose_name='收货联系人')
    receive_addr = models.CharField(max_length=256, verbose_name='收货地址')
    zip_code = models.CharField(max_length=10, verbose_name='邮政编码')
    is_default = models.BooleanField(default=False, verbose_name='默认地址')
    passport = models.ForeignKey('Passport', verbose_name='账户')

    objects = AddressManager()

    def __str__(self):
        return self.receive_name

    class Meta:
        db_table = 's_user_address'
