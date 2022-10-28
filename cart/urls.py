from django.urls import path
from .import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),

    path('checkout/', views.checkout, name='checkout'),
    path("coupon-apply", views.coupon_apply, name="coupon-apply"),
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_wishlist/<int:product_id>/', views.add_wishlist, name='add_wishlist'),
    path('remove_list/<int:product_id>/', views.remove_list, name='remove_list'),

]