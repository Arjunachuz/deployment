from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.views.decorators.cache import cache_control
from category.models import Category
from accounts.models import Account
from category.form import CategoryForm
from brand.models import Brand
from product.models import Product
from brand.form import BrandForm
from product.form import ProductForm
from orders.models import Order,OrderProduct,Payments,STATUS_1
from orders.models import BrandOffer, ProductOffer, CategoryOffer
from .forms import CategoryOfferForm, BrandOfferForm, ProductOfferForm
from user.forms import CouponForm, UsedCouponForm
from orders.models import Coupon, UsedCoupon
from django.db.models import Q,Count
from django.db.models.functions import ExtractMonth
import calendar
from django.template.loader import render_to_string
import csv
from django.http import HttpResponse
from accounts.pdf import html_to_pdf

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):

    if request.user.is_authenticated and request.user.is_superadmin:

         return redirect(adminhome)
    
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(email=username, password=password, is_superadmin=True)

        if user is not None and user.is_superadmin:
           
            auth.login(request, user)

            return redirect(adminhome)

        else:
            messages.error(request, 'invalid credential')

            return redirect(index)

    return render(request, 'admin/sign_in.html')

@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminhome(request):
    New = 0
    Accepted = 0
    Cancelled = 0
    Completed = 0
    Pending = 0
    if request.user.is_authenticated and request.user.is_superadmin:
        income = 0
        orders = Order.objects.all()
        for order in orders:
            income += order.order_total
        income = int(income)
        labels = []
        data = []
        orders = (
            OrderProduct.objects.annotate(month=ExtractMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .values("month", "count")
        )

        labels = [
            "jan",
            "feb",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
        ]
        data = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for d in orders:
            labels.append(calendar.month_name[d["month"]])
            data.append([d["count"]])
        labels1 = []
        data1 = []

        queryset = Order.objects.all()
        for i in queryset:
            if i.status == "New":
                New += 1
            elif i.status == "Accepted":
                Accepted += 1
            elif i.status == "Cancelled":
                Cancelled += 1
            elif i.status == "Completed":
                Completed += 1
            elif i.status == "Pending":
                Pending += 1
        print("cancelled list : ", Cancelled)

        labels1 = [
            "New",
            "Pending",
            "Accepted",
            "Cancelled",
            "Completed",
        ]
        data1 = [New, Pending, Accepted, Cancelled, Completed]
        print("status", Cancelled)

        order_count = OrderProduct.objects.count()
        product_count = Product.objects.count()
        print(product_count)
        cat_count = Category.objects.count()
        user_count = Account.objects.count()

        category = Category.objects.all().order_by("-id")
        products = Product.objects.all().order_by("-id")
        orderproducts = OrderProduct.objects.all().order_by("-id")

        context = {
            "cat_count": cat_count,
            "product_count": product_count,
            "order_count": order_count,
            "labels1": labels1,
            "data1": data1,
            "labels": labels,
            "data": data,
            "category": category,
            "products": products,
            "orderproducts": orderproducts,
            "income": income,
            "user_count": user_count,
        }
        return render(request, "admin/admin_home.html", context)
    else:
        redirect("/")




    
    
def adminlogout(request):

    auth.logout(request)

    return redirect(index)



@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def categoryList(request):

   if request.user.is_authenticated and request.user.is_superadmin:

    values = Category.objects.all().order_by('id')

    return render(request, 'admin/categorylist.html', {'values': values})
 


    
@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addcategory(request):
  
    if request.method == "POST":

        cat_form = CategoryForm(request.POST, request.FILES)

        if cat_form.is_valid():

            cat_form.save()
            messages.success(request, 'Your category has been added sucessfully')

        else:

            messages.error(request, 'Error')

        return redirect(categoryList)

    cat_form = CategoryForm()
    cats = Category.objects.all()
    context = {'cat_form': cat_form, 'cats': cats}

    return render(request, 'admin/addcategory.html', context)

 
    
@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editcategory(request, id):
   
    category = Category.objects.get(id=id)
    form = CategoryForm(instance=category)

    if request.method == 'POST':

        form = CategoryForm(request.POST, request.FILES, instance=category)

        if form.is_valid():

            form.save()

            return redirect(categoryList)
    else:

        return render(request, 'admin/categoryedit.html', {'form': form})
  
        

@login_required(login_url= '/')
def deletecategory(request, id):
   
    my_cat = Category.objects.get(id=id)
    my_cat.delete()

    return redirect(categoryList)

    

@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def brandList(request):

    if request.user.is_authenticated and request.user.is_superadmin:

        values = Brand.objects.all().order_by('id')

        return render(request, 'admin/brandlist.html', {'values': values})
   
    

@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addbrand(request):
    
    if request.method == "POST":

        brand_form = BrandForm(request.POST, request.FILES)

        if brand_form.is_valid():

            brand_form.save()
            messages.success(request, 'Your brand has been added sucessfully')

        else:

            messages.error(request, 'Error')

        return redirect(brandList)

    brand_form = BrandForm()
    brands = Brand.objects.all()
    context = {'brand_form': brand_form, 'brands': brands}

    return render(request, 'admin/addbrand.html', context)

   

@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editbrand(request, id):
   
        brand = Brand.objects.get(id=id)
        form = BrandForm(instance=brand)

        if request.method == 'POST':

            form = BrandForm(request.POST, request.FILES, instance=brand)

            if form.is_valid():

                form.save()

                return redirect(brandList)
        else:

            return render(request, 'admin/brandedit.html', {'form': form})
  
    
def deletebrand(request, id):
   
    my_brand = Brand.objects.get(id=id)
    my_brand.delete()

    return redirect(brandList)
    


# @login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def productList(request):

   if request.user.is_authenticated and request.user.is_superadmin:

    if "key" in request.GET:
        keyword = request.GET['key']
        if keyword:
            values = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))

    else:     

        values = Product.objects.all().order_by('id')

    return render(request, 'admin/productlist.html', {'values': values})
   

    
@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editproduct(request, id):
   
    product = Product.objects.get(id=id)
    form = ProductForm(instance=product)

    if request.method == 'POST':

        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():

            form.save()

            return redirect(productList)
    else:

        return render(request, 'admin/productedit.html', {'form': form})
 
    


@login_required(login_url= '/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addproduct(request):
   

    if request.method == "POST":

        prod_form = ProductForm(request.POST, request.FILES)

        if prod_form.is_valid():

            prod_form.save()
            messages.success(request, 'Your category has been added sucessfully')

        else:

            messages.error(request, 'Error')

        return redirect(productList)

    prod_form = ProductForm()
    context = {'prod_form': prod_form}

    return render(request, 'admin/addproduct.html', context)



def inactive_product(request, id):
   
        product_instance = Product.objects.get(id=id)
        product_instance.is_available=False
        product_instance.save()
        messages.success(request,'Product is Inactive')

        return redirect('productlist')

def active_product(request, id):
    
        product_instance = Product.objects.get(id=id)
        product_instance.is_available=True
        product_instance.save()
        messages.success(request, 'Product is Active')

        return redirect('productlist')

    
    
def userlist(request):
    
    if request.user.is_authenticated and request.user.is_superadmin:

        users = Account.objects.all().order_by('id')

        return render(request, 'admin/userlist.html', {'users': users})



def blockuser(request, id):
   
        user_instance = Account.objects.get(id=id)
        user_instance.is_active=False
        user_instance.is_blocked=True
        user_instance.save()
        messages.success(request,'user is successfully blocked')

        return redirect(userlist)

def unblockuser(request, id):
    
        user_instance = Account.objects.get(id=id)
        user_instance.is_active=True
        user_instance.is_blocked=False
        user_instance.save()
        messages.success(request, 'user is successfully unblocked')

        return redirect(userlist)



@login_required(login_url="/")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_display(request):

    if request.user.is_authenticated and request.user.is_superadmin:

        choices = STATUS_1

        if "key" in request.GET:

            search_key = (request.GET.get("key") 
            if request.GET.get("key") is not None else "")
            orders = Order.objects.order_by("id").filter(is_ordered=True).all() and Order.objects.filter(order_number__istartswith=search_key)
            context = {
                "orders": orders,
                "status": STATUS_1,
            }

            return render(request, "admin/orderadmin.html", context)

        else:

            orders = Order.objects.order_by("-id").all()
            order_products = OrderProduct.objects.all().order_by("-id")
            payment = Payments.objects.all()
            context = {
                "orders"        : orders,
                "order_products": order_products,
                "payment"       : payment,
                "status"        : STATUS_1,
                      }

            return render(request, "admin/orderadmin.html", context)

    else:

        return redirect("/")


@login_required(login_url="/")
def order_details_admin(request, id):

    if request.user.is_authenticated and request.user.is_superadmin:

        order_products = OrderProduct.objects.filter(order=id).order_by("-id")
        
        return render(request, "admin/orderdetailsadmin.html", {"order_products": order_products})

    else:

        return redirect("/")




@login_required(login_url="/")
def order_status(request, id):

    if request.user.is_authenticated and request.user.is_superadmin:

        status = request.POST.get("status")
        order = Order.objects.get(order_number=id)
        
        if order.status == "Cancelled":

            return redirect(order_display)

        else:

            if status == "Cancelled":

                order_products = OrderProduct.objects.filter(order__order_number=id)
                order.status = status
                order.save()
                
                for order_product in order_products:
                    order_product.product.stock += order_product.quantity
                    order_product.product.save()
                    messages.success(request, 'Status Updated')
            else:
                
                order.status = status
                order.save()
                messages.success(request, 'Status Updated')
                
         
        return redirect(order_display)

    else:

        return redirect("/")

def category_offer(request):
    if request.user.is_admin:
        offers = CategoryOffer.objects.all()
        context = {
            "offers": offers,
            "title" : "Category Offer",
        }
        return render(request, "admin/category_offer.html", context)
    else:
        messages.error(request, "invalid")
        return redirect("/")


@login_required(login_url="login")
def add_category_offer(request):
    if request.user.is_admin:
        if request.method == "POST":
            print(request.POST)
            form = CategoryOfferForm(request.POST)
            if form.is_valid():
                print("form is saved ")
                form.save()
                return redirect("category_offer")
            else:
                messages.warning(request, "form validation failed")
        else:
            form = CategoryOfferForm(request.POST)
            return render(request,"admin/add_category_offer.html",{"form": form,})
    else:
        return redirect("login")


@login_required(login_url="login")
def delete_category_offer(request, offer_id):
    if request.user.is_admin:
        CategoryOffer.objects.filter(pk=offer_id).delete()
        messages.info(request, "Category Offer Deleted")
        return redirect("category_offer")
    else:
        messages.info(request, "Invalid")
        return redirect("admin-login")


@login_required(login_url="login")
def product_offers(request):
    if request.user.is_admin:
        offers = ProductOffer.objects.all()
        context = {
            "offers": offers,
            "title" : "Category Offer",
        }
        return render(request, "admin/product_offer.html", context)
    else:
        messages.error(request, "invalid")
        return redirect("/")


@login_required(login_url="login")
def add_product_offer(request):
    if request.user.is_admin:
        if request.method == "POST":
            print(request.POST)
            form = ProductOfferForm(request.POST)
            if form.is_valid():
                print("form is saved ")
                form.save()
                return redirect("product_offers")
            else:
                messages.warning(request, "form validation failed")
        else:
            form = ProductOfferForm(request.POST)
            return render(request,"admin/add_product_offer.html",{"form": form,})
    else:
        return redirect("login")


@login_required(login_url="login")
def delete_product_offer(request, offer_id):
    if request.user.is_admin:
        ProductOffer.objects.filter(pk=offer_id).delete()
        messages.info(request, "Offer Deleted")
        return redirect("product_offers")
    else:
        messages.info(request, "Invalid")
        return redirect("admin-login")


@login_required(login_url="login")
def brand_offers(request):
    if request.user.is_admin:
        offers = BrandOffer.objects.all()
        context = {
            "offers": offers,
            "title": "Brand Offer",
        }
        return render(request, "admin/brand_offer.html", context)
    else:
        messages.error(request, "invalid")
        return redirect("/")


@login_required(login_url="login")
def add_brand_offer(request):
    if request.user.is_admin:
        if request.method == "POST":
            print(request.POST)
            form = BrandOfferForm(request.POST)
            if form.is_valid():
                print("form is saved ")
                form.save()
                return redirect("brand_offers")
            else:
                messages.warning(request, "form validation failed")
        else:
            form = BrandOfferForm(request.POST)
            return render(request,"admin/add_brand_offer.html",{"form": form,})
    else:
        return redirect("login")


@login_required(login_url="login")
def delete_brand_offer(request, offer_id):
    if request.user.is_admin:
        BrandOffer.objects.filter(pk=offer_id).delete()
        messages.info(request, "Brand Offer Deleted")
        return redirect("brand_offers")
    else:
        messages.info(request, "Invalid")
        return redirect("admin-login")

def view_coupon(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        values = Coupon.objects.all()
        return render(request, "admin/couponlist.html", {"values": values})
    else:
        return redirect("/")


def delete_coupon(request, id):
    if request.user.is_authenticated and request.user.is_superadmin:
        my_coupon = Coupon.objects.get(id=id)
        my_coupon.delete()
        return redirect(view_coupon)
    else:
        return redirect("/")


def add_coupon(request):
    if request.user.is_authenticated and request.user.is_superadmin:

        if request.method == "POST":
            coupon_form = CouponForm(request.POST, request.FILES)
            if coupon_form.is_valid():
                coupon_form.save()
                messages.success(request, "Your coupon has been added sucessfully")
            else:
                messages.error(request, "Error")

            return redirect(view_coupon)
        coupon_form = CouponForm()

        context = {"coupon_form": coupon_form}
        return render(request, "admin/addcoupon.html", context)

    return redirect("/")

def sales_report(request):
    product = Product.objects.all()
    context = {"product": product}
    return render(request, "admin/salesreport.html", context)


def sales_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=products.csv"

    writer = csv.writer(response)
    products = Product.objects.all().order_by("-id")

    writer.writerow(
        [
            "Product",
            "Brand",
            "Category",
            "Stock",
            "Price",
            "Sales Count",
            "Revenue",
            "Profit",
        ]
    )

    for product in products:
        writer.writerow(
            [
                product.product_name,
                product.brand.brand_name,
                product.category.category_name,
                product.stock,
                product.price,
                product.get_count()[0]["quantity"],
                product.get_revenue()[0]["revenue"],
                product.get_profit(),
            ]
        )
    return response


def sales_export_pdf(request):
    product = Product.objects.all()
    open("templates/admin/pdf_out.html", "w", encoding="utf-8").write(
        render_to_string("admin/sales_export_pdf.html", {"product": product})
    )
    pdf = html_to_pdf("admin/pdf_out.html")
    return HttpResponse(pdf, content_type="application/pdf")
