from ast import keyword
from distutils.command.build_scripts import first_line_re
import requests
from itertools import product
from multiprocessing import context
import re
from telnetlib import STATUS
from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages, auth
from django.views.decorators.cache import cache_control
from setuptools import PEP420PackageFinder
from category.models import Category
from accounts.models import Account, UserProfile
from brand.models import Brand
from .models import *
from .mixins import *
import random
from .forms import RegistrationForm,UserForm,UserProfileForm
from product.models import Product
from cart.models import Cart,CartItem,WishListItem
from orders.models import Order, OrderProduct
from cart.views import _cart_id
from django.core.paginator import Paginator
from orders.models import BrandOffer, CategoryOffer, ProductOffer
from django.db.models import  Q





# Create your views here.

def user_login(request):
  
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
  
        user = auth.authenticate(email = email, password = password)
        
        if user is not None:

            try:
                
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exist:

                    cart_item = CartItem.objects.filter(cart=cart)
                    

                    for item in cart_item:

                        item.user = user
                        item.save()

            except:
                

                pass    
            messages.error(request, 'Succesfully loged in') 
            auth.login(request, user)


            url = request.META.get('HTTP_REFERER')
            print('url',url)

            try:
                query = requests.utils.urlparse(url).query 
                print('query',query)              #next=/cart/checkout
                params = dict(x.split('=') for x in query.split('&'))             # {'next': 'cart/checkout'}
                if 'next' in params:
                    nextPage = params['next']
                    print('next page',nextPage)     # cart/checkout
                    return redirect(nextPage)
            except:  
                # messages.error(request, 'Succesfully loged in')  
                return redirect('home')
        else :
            messages.error(request, 'User does not match')  
            return redirect('loginpage')  
    return render(request, 'user/sign_in.html') 


def register(request):
    if request.method == 'POST':

         form = RegistrationForm(request.POST)

         if form.is_valid():

            first_name       = form.cleaned_data['first_name']
            last_name        = form.cleaned_data['last_name']
            email            = form.cleaned_data['email']
            phone_number     = form.cleaned_data['phone_number']
            password         = form.cleaned_data['password']
            username         = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,phone_number=phone_number,username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # Create User Pofile 

            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/user profile.jpg'
            profile.save()

            request.session['phone_number'] = phone_number
            send(phone_number)

            return redirect('otpverify')

        #  else:

        #         form = RegistrationForm()

        #         context={'form' : form}
        
        #         return render(request,'user/register.html',context)
    else:

        form = RegistrationForm()

    context={'form' : form}
        
    return render(request,'user/register.html',context)



def userhome(request):

    product= Product.objects.all()[:4]

    context={'product':product}

    return render(request,'user/index.html', context)  



def shop(request, slug=None):
    
    
    user_instance = request.user
    products = Product.objects.all()
    for item in products:
        
        
        p_offer = 0
        c_offer = 0
        b_offer = 0
        
            
        if BrandOffer.objects.filter(brand=item.brand).exists():
            brand = (BrandOffer.objects.filter(brand=item.brand).order_by("-brand_offer").first())
            b_offer = brand.brand_offer
           
        if ProductOffer.objects.filter(product=item).exists():
            product_ = (ProductOffer.objects.filter(product=item).order_by("-product_offer").first())
            p_offer = product_.product_offer
           
        if CategoryOffer.objects.filter(category=item.category).exists():
            category_ = (CategoryOffer.objects.filter(category=item.category).order_by("-category_offer").first())
            c_offer = category_.category_offer

        offer_ = [p_offer, c_offer, b_offer]
        
        offer = max(offer_)
       
        item.offer = offer
       
        item.save()  # save product
        
               
        
    
    
    if slug is not None:

        if (Category.objects.filter(slug=slug)):
        
            product_category= Product.objects.filter(category__slug=slug)
            paginator = Paginator(product_category, 6)
            page = paginator.get_page(1)
            
        else:
           
            product_brand= Product.objects.filter(brand__slug=slug)
            paginator = Paginator(product_brand, 6)
            page = paginator.get_page(1)

    else:
        
        product_all= Product.objects.all()
        paginator = Paginator(product_all, 6)
        page_num = request.GET.get('page')
        page = paginator.get_page(page_num)
    
    
    context = {'category': Category.objects.all(),
                'brand'  : Brand.objects.all(),
                'page'   : page}
    print(page)

    return render(request, 'user/shop.html', context)
    
 
def shop_details(request, id):

    if request.user.is_authenticated:

        product = Product.objects.get(id=id)
        in_cart = CartItem.objects.filter(user=request.user,product=product)
        print(in_cart)
        in_list = WishListItem.objects.filter(product=product, user=request.user).exists()

        context = {'product': product,
                   'in_cart': in_cart,
                   'in_list': in_list}
        
        return render(request, 'user/shop-details.html', context)

    else:    

        product = Product.objects.get(id=id)
        in_cart = CartItem.objects.filter(cart__cart_id= _cart_id(request), product=product).exists()

        context = {'product': product,
                   'in_cart': in_cart}
        
        return render(request, 'user/shop-details.html', context)
 
def otpverify(request):

    if request.method == 'POST':

       phone_otp = request.POST['otp']
       user = Account.objects.get(phone_number=request.session['phone_number'])

       if check(request.session['phone_number'],phone_otp):

           user.is_active=True
           user.is_phone_verified=True
           user.save()
           messages.error(request,'Registered Succesfully')
           return redirect('loginpage')

       else:

           print('failed')
           messages.error(request,'otp verification failed')
           user.delete()
           return redirect(register)
           
    else:

        return render(request,'user/otp_verify.html')


@login_required(login_url='loginpage')
def dashboard(request):

    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'orders_count': orders_count,
        'userprofile' : userprofile,
              }

    return render(request, 'user/dashboard.html',context)
    

@login_required(login_url='loginpage')
def my_orders(request):
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {'orders':orders}

    return render(request, 'user/my_orders.html', context)   

@login_required(login_url='loginpage')
def edit_profile(request):

    userprofile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been upadated.')

            return redirect('edit_profile')

    else:
        
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)        

    context = {
        'user_form'   : user_form,
        'profile_form': profile_form,
        'userprofile ': userprofile,
              }    

    return render(request, 'user/edit_profile.html', context)    


@login_required(login_url='loginpage')
def change_password(request):

    if request.method == 'POST':

        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user =Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:

            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been Updated')

                return redirect('change_password')

            else:
                messages.error(request, 'Please enter valid Current Password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')    
            return redirect('change_password')        

         

    return render(request, 'user/change_password.html')  


@login_required(login_url='loginpage')
def order_detail(request, order_id):

    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal  += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }

    return render(request, 'user/order_detail.html', context)


def order_cancel(request, order_id):
    
    order = Order.objects.get(user=request.user,order_number=order_id, is_ordered = True)
    ordered_product = OrderProduct.objects.filter(order_id=order.id)

    for item in ordered_product:
        product = Product.objects.get(id=item.product_id)
        product.stock += item.quantity
        product.save()
        item.ordered = 'False'
        item.save()

    order.status = 'Cancelled'
    order.payment.status = 'Cancelled'    
    order.is_ordered = 'False'
    order.save()
    

    return redirect('my_orders')    




   





def search(request):

    page = 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            product = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            paginator = Paginator(product, 6)
            page = paginator.get_page(1)

    context = {
        'category' : Category.objects.all(),
        'brand'    : Brand.objects.all(),
        'page'     : page,
               }
               
    return render(request, 'user/shop.html',context)
   
def blog(request):
    return render(request, 'user/blog.html')   


def logout(request):
    messages.error(request, 'Logged Out ! ') 
    auth.logout(request) 
    request.session.flush()
    return redirect('home')       
        
    
