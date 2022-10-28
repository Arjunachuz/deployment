from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from cart.models import CartItem
from product.models import Product
from .forms import OrderForm
from .models import Order, OrderProduct, Payments
import  datetime
import json
from .models import Coupon, UsedCoupon

# Create your views here.

def place_order(request, total=0, quantity=0):

    current_user = request.user
    

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        
        return redirect('cart')

    grand_total = 0
    tax = 0 
    reduction = 0 
    coupon = 0
    coupon_code = 0 

    if "coupon_code" in request.session:
            coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])
            request.session["coupon_code"]
            coupon_code = reduction = coupon.discount

    else:
            coupon = "No Coupon"
            reduction = 0

    for cart_item in cart_items:

        if cart_item.product.offer ==0 :
              total += (cart_item.product.price * cart_item.quantity)
        else:
              total += (cart_item.product.offer * cart_item.quantity) 
        quantity += cart_item.quantity

    tax = (4 * total)/100
    grand_total =total + tax - reduction
         

    if request.method == 'POST':
        
        form = OrderForm(request.POST)   
        
        if form.is_valid():
            
            data = Order()
            
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')       # to get the ip of user
            data.save()
           
            # generate order number

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")

            order_number = current_date + str(data.id)

            request.session["ordernumber"] = order_number

            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order'      :order,
                'cart_items' :cart_items,
                'total'      :total,
                'tax'        :tax,
                'grand_total':grand_total,
                 "coupon"    : coupon,
                'coupon_code': coupon_code
                      }

            return render(request, 'user/payments.html', context)

    else:

        return redirect('checkout')       

    return render(request, 'user/index.html')     



def payments(request):

    body = json.loads(request.body)
    
    order = Order.objects.get(user=request.user, is_ordered= False, order_number=body['orderID'])
    payment = Payments(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
                     )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()
            
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

    CartItem.objects.filter(user=request.user).delete()  

    # send datas back to 'sendData method '  

    data = {
        'order_number': order.order_number,
        'transID'     : payment.payment_id,
           }

    return JsonResponse(data)

        

    return render(request, 'user/payments.html')
     


def order_complete(request):
     
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:

        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payments.objects.get(payment_id=transID)

        subtotal = 0 
    
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        
        context = {
             'order'          : order,
             'ordered_product': ordered_products,
             'order_number'   : order.order_number,
             'transID'        : payment.payment_id,
             'payment'        : payment,
             'subtotal'       : subtotal, 
             
        }

        if "coupon_code" in request.session:
            print("coupon found ")
            used_coupons = UsedCoupon()
            coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])
            print(coupon)
            used_coupons.coupon = coupon
            used_coupons.user = request.user
            used_coupons.save()
            print(request.session["coupon_code"])
            del request.session["coupon_code"]

        return render(request, 'user/order_complete.html', context)

    except (Payments.DoesNotExist, Order.DoesNotExist):

        return redirect('home')    


def payment_cod(request):

    if request.user.is_authenticated:

        current_user = request.user

        # generate order number
        order_number = request.session["ordernumber"]
       
        # move cart items to order product table

        cart_items = CartItem.objects.filter(user=current_user)

        order = Order.objects.get( user=request.user, is_ordered=False, order_number=order_number)
        
        # save payment informations
        payment = Payments(
            user=current_user,
            payment_method="Cash On Delivery",
            amount_paid=order.order_total,
            status="Pending",
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()
            
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()
       
        return redirect("order_complete_cod")

    else:

        return redirect("/")



def order_complete_cod(request):
    
    if request.user.is_authenticated:
        
        order_number = request.session["ordernumber"]
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        offer = 0

        for i in ordered_products:
            subtotal += i.product_price * i.quantity
            offer += (i.product.offer * i.quantity)
        offer_price = order.order_total - offer  

        context = {
            "order"           : order,
            "ordered_products": ordered_products,
            "order_number"    : order_number,
            "subtotal"        : subtotal,
            'offer'           : offer,
            'offer_price'     : offer_price,
                  }
        if "coupon_code" in request.session:
            print("coupon found ")
            used_coupons = UsedCoupon()
            coupon = Coupon.objects.get(coupon_code=request.session["coupon_code"])
            print(coupon)
            used_coupons.coupon = coupon
            used_coupons.user = request.user
            used_coupons.save()
            print(request.session["coupon_code"])
            del request.session["coupon_code"]          

        return render(request, "user/cod_order_complete.html", context)

    else:

        return redirect("/")


    