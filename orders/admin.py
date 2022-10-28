from itertools import product
from django.contrib import admin
from.models import BrandOffer, CategoryOffer, Order,Payments,OrderProduct, ProductOffer

# Register your models here.

class OrderProductInline(admin.TabularInline):

    model = OrderProduct
    readonly_fields = ('payment','user','product','quantity','product_price','ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','phone','email','city','order_total','tax','status','is_ordered','created_at']
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name','phone','email']
    list_per_page = 20
    inlines = [OrderProductInline]



admin.site.register(Order, OrderAdmin)
admin.site.register(Payments)
admin.site.register(OrderProduct)
admin.site.register(BrandOffer)
admin.site.register(CategoryOffer)
admin.site.register(ProductOffer)
