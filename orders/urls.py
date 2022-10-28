from django.urls import path
from . import views

urlpatterns = [
    
    path('place_order/',views.place_order, name='place_order'),
    path('payments/',views.payments, name='payments'),
    path('order_complete/',views.order_complete, name='order_complete'),
    path("cod/", views.payment_cod, name="payment_cod"),
    path("order-complete-cod/", views.order_complete_cod, name="order_complete_cod"),
   
    
]