from django.contrib import admin
from .models import Coupon, UsedCoupon

# Register your models here.

class CouponAdmin(admin.ModelAdmin):
    list_display = ("coupon_code", "discount", "is_active")


class UsedCouponAdmin(admin.ModelAdmin):
    list_display = ("user", "coupon")


admin.site.register(Coupon, CouponAdmin)
admin.site.register(UsedCoupon, UsedCouponAdmin)
