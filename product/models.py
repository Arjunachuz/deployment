# from asyncio.windows_events import NULL
# from curses.ascii import NUL
from asyncio.windows_events import NULL
from email.policy import default
from django.db import models
from django.utils import timezone
from django.apps import apps
from django.db.models import Sum


# Create your models here.
from brand.models import Brand
from category.models import Category
import uuid


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(max_length=500, blank=True)
    details = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='pics/products')
    images1 = models.ImageField(upload_to='pics/products')
    images2 = models.ImageField(upload_to='pics/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    offer = models.IntegerField(default=None)

    def __str__(self):
        return self.product_name

    def get_count(self, month=timezone.now().month):
        orderproduct = apps.get_model("orders", "OrderProduct")
        order = orderproduct.objects.filter(product=self, created_at__month=month)
        return order.values("product").annotate(quantity=Sum("quantity"))

    def get_revenue(self, month=timezone.now().month):
        orderproduct = apps.get_model("orders", "OrderProduct")
        orders = orderproduct.objects.filter(product=self, created_at__month=month)
        return orders.values("product").annotate(revenue=Sum("product_price"))

    def get_profit(self, month=timezone.now().month):
        orderproduct = apps.get_model("orders", "OrderProduct")
        orders = orderproduct.objects.filter(product=self, created_at__month=month)
        profit_calculted = orders.values("product").annotate(
            profit=Sum("product_price")
        )
        profit_calculated = profit_calculted[0]["profit"] * 0.23
        return profit_calculated    