from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='loginpage'),
    path('register',views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('',views.userhome,name='home'),
    path('otpverify/',views.otpverify,name='otpverify'),
    path('shop/',views.shop,name='shop'),
    path('shop/<str:slug>',views.shop,name='shop'),
    path('shop-details/<int:id>',views.shop_details,name='shop-details'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('my_orders/',views.my_orders, name='my_orders'),
    path('edit_profile/',views.edit_profile, name='edit_profile'),
    path('change_password/',views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/',views.order_detail, name='order_detail'),
    path('order_cancel/<int:order_id>/',views.order_cancel, name='order_cancel'),
   

    path('search/', views.search, name='search'),
    path('blog/', views.blog, name='blog')
   
   
    
]