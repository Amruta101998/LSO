from django.db import models

# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import User



class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100 )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=200)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images", default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000, null=True,blank=True)
    userId = models.IntegerField(default=0)
    amount = models.IntegerField(default=0, null=True,blank=True)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111,null=True,blank=True)
    address = models.CharField(max_length=111,null=True,blank=True)
    city = models.CharField(max_length=111,null=True,blank=True)
    state = models.CharField(max_length=111,null=True,blank=True)
    zip_code = models.CharField(max_length=111,null=True,blank=True)
    phone = models.CharField(max_length=111, default="",null=True,blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.update_desc

class Review(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    comment = models.TextField(max_length=250)
    rate = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)
    
class Coupon(models.Model):
    order_id = models.ForeignKey(Orders, models.CASCADE)
    code = models.TextField(max_length=30)
    amount = models.IntegerField(max_length=300)

    def __str__(self):
        return self.order_id