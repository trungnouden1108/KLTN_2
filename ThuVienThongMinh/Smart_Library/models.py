from django.db import models
from django.utils import timezone
import datetime
import serial
import pytz

# Create your models here.
class DocGia(models.Model):
    id_DG = models.CharField(max_length=8,blank=False,null=False,default="")
    ten_DG = models.CharField(max_length=100,blank=False,null=False)
    email_DG = models.EmailField(max_length=200,blank=False,null=False)
    CMND=models.CharField(max_length=20,blank=False,null=False)
    phone=models.CharField(max_length=15,blank=False,null=False)
    image_user=models.ImageField(upload_to='image_user/',blank=True,null=True)
    money_user = models.IntegerField(blank=True,default=10000)
    time_create=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.id_DG

class ID_DocGia(models.Model):
    Id_Docgia=models.CharField(max_length=8,blank=True,default="")

    def __str__(self):
        return self.Id_Docgia

class ID_Book(models.Model):
    id_Book=models.CharField(max_length=8,blank=True,default="")

    def __str__(self):
        return self.id_Book
# Models Loại Sách
class Category_Book(models.Model):
    title = models.CharField(default='',max_length=255)
    #slug = models.CharField(max_length=100,default='')
    #description = models.TextField(default='')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# Model Sách
class Book(models.Model):
    id_book=models.CharField(max_length=8,default='',blank=False,null=False)
    title = models.CharField(max_length=255,default='',blank=False,null=False)
    category = models.ForeignKey(Category_Book,on_delete=models.CASCADE)
    description = models.TextField(default='',blank=False,null=False)
    sl = models.IntegerField(default=0,blank=True)
    image_book=models.ImageField(upload_to='image_book/',blank=True,null=True)
    author=models.CharField(default='',blank=True,max_length=50)
    active = models.BooleanField(default=True)
    dup=models.BooleanField(default=False,blank=True)
    new=models.BooleanField(default=False,blank=True)
    rate = models.IntegerField(blank=True, default=0)
    vote = models.IntegerField(blank=True, default=0)
    ave_rate=models.IntegerField(blank=True,default=0)
    time_create=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Model Giỏ hàng
class Cart(models.Model):
    tz_hcm = pytz.timezone('Asia/Ho_Chi_Minh')
    id_user=models.CharField(max_length=10,default='')
    id_bor1=models.CharField(max_length=14,default='',blank=True)
    create1=models.DateTimeField(default=(datetime.datetime.now(tz_hcm)+datetime.timedelta(hours=7)))
    id_bor2=models.CharField(max_length=14,default='',blank=True)
    create2=models.DateTimeField(default=(datetime.datetime.now(tz_hcm)+datetime.timedelta(hours=7)))
    id_bor3=models.CharField(max_length=14,default='',blank=True)
    create3=models.DateTimeField(default=(datetime.datetime.now(tz_hcm)+datetime.timedelta(hours=7)))


    #created_at=models.DateTimeField(default=(datetime.datetime.now(tz_hcm)+datetime.timedelta(hours=7)))

    def __str__(self):
        return self.id_user

class Check_book(models.Model):
    id_bor=models.CharField(max_length=14,blank=True,default='')

    def __str__(self):
        return self.id_bor

class Contact(models.Model):
    name = models.CharField(max_length=100,blank=False,null=False)
    mail = models.EmailField(max_length=200,blank=False,null=False)
    phone=models.CharField(max_length=15,blank=False,null=False)
    opinion=models.TextField(max_length=5000,blank=False,null=False)

    def __str__(self):
        return self.name

