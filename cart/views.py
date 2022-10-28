
from multiprocessing import context
from django.shortcuts import get_object_or_404, redirect, render
from product.models import Product
from cart.models import Cart, CartItem, WishListItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from orders.models import Coupon, UsedCoupon
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.

def _cart_id(request):

    cart = request.session.session_key

    if not cart:

        cart = request.session.create()

    return cart


def add_cart(request, product_id):
    
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:

        try:

            cart_item = CartItem.objects.get(product=product, user=current_user)
            cart_item.quantity += 1
            cart_item.save()

        except CartItem.DoesNotExist:   

            cart_item = CartItem.objects.create(product=product, quantity = 1, user=current_user)
            cart_item.save()  

        return redirect('cart')

    else:    

        try:
            
            cart = Cart.objects.get(cart_id=_cart_id(request))


        except Cart.DoesNotExist:


            cart = Cart.objects.create(cart_id = _cart_id(request))
            cart.save()
        
        try:

            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()

        except CartItem.DoesNotExist:   

            cart_item = CartItem.objects.create(product=product, quantity = 1, cart= cart)
            cart_item.save()  

        return redirect('cart')    

def remove_cart(request, product_id):

    # cart = Cart.objects.get(cart_id =_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:

         cart_item = CartItem.objects.get(product=product, user=request.user)
    else:     
          
         cart = Cart.objects.get(cart_id =_cart_id(request))
         cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1 :

        cart_item.quantity -= 1
        cart_item.save()

    else:

        cart_item.delete()   

    return redirect('cart')    


def remove_cart_item(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:

        cart_item = CartItem.objects.get(product=product, user=request.user)

    else:    
        cart = Cart.objects.get(cart_id =_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
        
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):

    tax=0
    grand_total=0
    reduction = 0
    coupon_code = 0
    coupon = 0
  

    try:

        if request.user.is_authenticated:

            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

            if "coupon_code" in request.session:

                coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])
                coupon_code = request.session["coupon_code"]
                reduction = coupon.discount

            else:
                coupon = "No Coupon"
                reduction = 0
        else:    

            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            if cart_item.product.offer ==0 :
              total += (cart_item.product.price * cart_item.quantity)
            else:
              total += (cart_item.product.offer * cart_item.quantity) 
            quantity += cart_item.quantity
            

        tax = (4 * total)/100
        grand_total =total + tax - reduction
        

    except ObjectDoesNotExist:

        pass 

    context ={
        'total'      : total,
        'quantity'   : quantity,
        'cart_items' : cart_items,
        'tax'        : tax,
        'grand_total':grand_total,
        "coupon"     : coupon,
        'coupon_code': coupon_code,
        
        
             }    

    return render(request, 'user/cart.html',context)

@login_required(login_url='loginpage')
def checkout(request, total=0, quantity=0, cart_items=None): 

    tax=0
    grand_total=0
    reduction = 0
    coupon = None

    try:

        if request.user.is_authenticated:

            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
            if "coupon_code" in request.session:

                    coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])
                    reduction = coupon.discount

            else:
                    reduction = 0
                    coupon = "No Coupon"
        else:    

            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
             
        for cart_item in cart_items:
            if cart_item.product.offer ==0 :
              total += (cart_item.product.price * cart_item.quantity)
            else:
              total += (cart_item.product.offer * cart_item.quantity) 
            quantity += cart_item.quantity

        tax = (4 * total)/100
        grand_total =total + tax - reduction
          

    except ObjectDoesNotExist:

        pass 

    context ={
        'total'       : total,
        'quantity'    : quantity,
        'cart_items'  : cart_items,
        'tax'         : tax,
        'grand_total' :grand_total,
        "coupon"      : coupon,


    }    
    return render(request, 'user/checkout.html', context)  

def coupon_apply(request):
    if request.method == "POST":

        coupon_code = request.POST.get("coupon_code")

        try:
            if "coupon_code" in request.POST:
                if Coupon.objects.get(coupon_code=coupon_code):
                    coupon_exist = Coupon.objects.get(coupon_code=coupon_code)
                    try:
                        used_coupon = UsedCoupon.objects.get(
                            user=request.user, coupon=coupon_exist
                        )
                        if used_coupon is not None:
                            print("fail")
                            messages.error(request, "coupon already used")
                            return redirect(cart)

                    except:

                        print("pass")
                        request.session["coupon_code"] = coupon_code
                        return redirect("cart")
            else:
                pass
        except:
            messages.error(request, "invalid Coupon ")
            return redirect("cart")

    return redirect(cart)

def  remove_coupon(request):
    del request.session['coupon_code']    
    return redirect('cart')    


@login_required(login_url='loginpage')
def wishlist(request):

    if request.user.is_authenticated:
        
        
        list_items= WishListItem.objects.filter(user=request.user, is_active=True)
        paginator = Paginator(list_items, 8)
        page_num = request.GET.get('page')
        page = paginator.get_page(page_num)

    context = {'page':page}
    

    return render(request,'user/wishlist.html',context)


@login_required(login_url='loginpage')
def add_wishlist(request, product_id):
    
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:

            list_item = WishListItem.objects.create(product=product, user=current_user)
            
            list_item.save()

            return redirect('wishlist')

@login_required(login_url='loginpage')
def remove_list(request, product_id):

    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:

            list_item = WishListItem.objects.get(product=product, user=current_user)
            list_item.delete()

            return redirect('wishlist')            


        

