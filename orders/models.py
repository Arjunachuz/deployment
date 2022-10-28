import email
from email.policy import default
from random import choices
from telnetlib import STATUS
from django.db import models
from accounts.models import Account
from product.models import Product
from brand.models import Brand
from category.models import Category

# Create your models here.

STATUS_1 =(
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
    )   

class Payments(models.Model):

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


    def _str_(self):
        return (self.payment_id)


class Order(models.Model):

    STATUS =(
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
    )   

    
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payments, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    offer = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='New')
    ip = models.CharField(max_length=20, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def _str_(self):
        return self.first_name

        
class OrderProduct(models.Model):

    order =  models.ForeignKey(Order, on_delete=models.CASCADE)     
    payment = models.ForeignKey(Payments, on_delete=models.SET_NULL, blank=True, null=True)  
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.IntegerField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def _str_(self):
        return self.product.product_name


class CategoryOffer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    category_offer = models.IntegerField(default=0, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BrandOffer(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, blank=True, null=True)
    brand_offer = models.IntegerField(default=0, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    product_offer = models.IntegerField(default=0, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10, blank=True)
    discount = models.FloatField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.coupon_code


class UsedCoupon(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True)

