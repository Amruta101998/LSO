from multiprocessing import context
import re
from tkinter import EXCEPTION

from django.views import View
from shop.models import Profile
from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpResponseRedirect
import uuid
# from django.http import HttpResponse
from .models import Product, Contact, Orders, OrderUpdate, Review
from django.contrib.auth.models import User
from django.contrib import messages
from math import ceil
from django.contrib.auth import authenticate, login, logout
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from PayTm import Checksum
#MERCHANT_KEY = 'kbzk1DSbJiV_O3p5';
MERCHANT_KEY = 'BAgmHldaqstQorPX';

def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    lso = {'allProds': allProds}
    return render(request, 'shop/index.html', lso)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
        return render(request, 'shop/contact.html', {'thank': thank})
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        password = request.POST.get('password')
        user = authenticate(username=name, password=password)
        if user is not None:
            try:
                order = Orders.objects.filter(order_id=orderId, email=email)
                if len(order) > 0:
                    update = OrderUpdate.objects.filter(order_id=orderId)
                    updates = []
                    for item in update:
                        updates.append({'text': item.update_desc, 'time': item.timestamp})
                        response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                    return HttpResponse(response)
                else:
                    return HttpResponse('{"status":"noitem"}')
            except Exception as e:
                return HttpResponse('{"status":"error"}')
        else:
            return HttpResponse('{"status":"Invalid"}')
    return render(request, 'shop/tracker.html')


def orderView(request):
    if request.user.is_authenticated:
        current_user = request.user
        orderHistory = Orders.objects.filter(userId=current_user.id)
        if len(orderHistory) == 0:
            messages.info(request, "You have not ordered.")
            return render(request, 'shop/orderView.html')
        return render(request, 'shop/orderView.html', {'orderHistory': orderHistory})
    return render(request, 'shop/orderView.html')


def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower() or query in item.desc or query in item.product_name or query in item.category or query in item.desc.upper() or query in item.product_name.upper() or query in item.category.upper():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    lso = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query) < 3:
        lso = {'msg': "No item available. Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', lso)


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        user_id = request.POST.get('user_id', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, userId=user_id, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been Placed")
        update.save()
        thank = True
        id = order.order_id

        if 'onlinePay' in request.POST:
            # Request paytm to transfer the totalPrice to your account after payment by user
            lso_dict = {

                # 'MID': 'WorldP64425807474247',
                'MID': 'BSGKaY34965531522665',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

            }
            lso_dict['CHECKSUMHASH'] = Checksum.generate_checksum(lso_dict, MERCHANT_KEY)
            return render(request, 'shop/paytm.html', {'lso_dict': lso_dict})
        elif 'cashOnDelivery' in request.POST:
            return render(request, 'shop/checkout.html', {'thank': thank, 'id': id})
        


    return render(request, 'shop/checkout.html')

def productView(request, myid):
    product = Product.objects.get(id=myid)
    # print(product)
    #return render(request, 'shop/prodView.html', {'product': product[0]})
    review = Review.objects.filter(product_id=myid)
    user = request.user
    qty =0
    context= {
        "reviews" : review,
        "qty": qty,
        "product": product,
    }
    #print(context)
    return render(request, 'shop/prodView.html', context)



def handeLogin(request):
    if request.method == "POST":
        # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        myuser = User.objects.filter(username = loginusername).first()
        if myuser is None:
            messages.success(request, 'User not found.')
            return redirect('/shop/login')

        profile_obj = Profile.objects.filter(user = myuser ).first()

        if not profile_obj.is_verified:
            messages.success(request, 'Profile is not verified check your mail.')
            return redirect('/shop/login')


        user = authenticate(username=loginusername, password=loginpassword)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect('/shop/')
        else:
            messages.warning(request, "Invalid credentials! Please try again")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return HttpResponse("404- Not found")


def handleSignUp(request):
    if request.method == "POST":
        # Get the post parameters
        username = request.POST['username']
        f_name = request.POST['f_name']
        l_name = request.POST['l_name']
        email = request.POST['email1']
        phone = request.POST['phone']
        password = request.POST['password']
        password1 = request.POST['password1']

        phnpatternvalidation =re.compile('^[6789]\d{9}$')

        if len(phone)> 10  or len(phone)< 10:
            messages.warning(request, "Phone No is not correct")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if (phnpatternvalidation.search(phone) == None):
            messages.warning(request, "Unable to SignUp. Phone No. is Invalid")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # pattern="^[789] || ^[860] || ^[989]"
        # phonepattern = "*[0-9]"
        # if len(phone)> 10  or len(phone)< 10 and re.findall(pattern,phonepattern,phone):
        #     messages.warning(request, "Phone No is not correct")
        #     return redirect('/shop/signup')
        # if re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$", password):
        #         messages.warning(request, " Passwords match")
        # else:
        #         messages.warning(request, " Passwords do not match")
        #         return redirect('/shop/signup')
        if(password!=password1):
            messages.warning(request, " Passwords do not match")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if(User.objects.filter(username=username).exists()):
            messages.warning(request, " Username Already taken. Try with different Credentials.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # elif(User.objects.filter(email=email).exists()):
        #     messages.warning(request, " Email Already taken. Try with different Credentials.")
        #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            myuser = User.objects.create_user(username=username, email=email, password=password)
            myuser.first_name = f_name
            myuser.last_name = l_name
            myuser.phone=phone
            myuser.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user = myuser , auth_token = auth_token)
            profile_obj.save()
            send_mail_after_registration(email , auth_token)
            return redirect('/shop/token')
    else:
        return HttpResponse("404 - Not found")

def success(request):
    return render(request , 'shop/success.html')


def token_send(request):
    return render(request , 'shop/token_send.html')



def verify(request , auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
    

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                userr=User.objects.get(id=profile_obj.user_id)
                login(request,userr)
                return redirect('/shop/')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            userr=User.objects.get(id=profile_obj.user_id)
            login(request,userr)
            return redirect('/shop/')
        else:
            return HttpResponse("404 - Not found")
    except Exception as e:
        print(e)
        return redirect('/shop/')


def send_mail_after_registration(email , token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/shop/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list )
    


def handleLogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def Review_rate(request):
    if request.method == "GET":
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        comment =request.GET.get('comment')
        rate =request.GET.get('rate')
        user = request.user
        Review(user=user, product=product, comment= comment, rate=rate).save()
        return redirect(f'/shop/productView/{product_id}',id=product_id)


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})

def addPromoCode(request):
    if request.method == 'POST':
        try:
            form = request.POST
            print(form)
        except Exception as e:
            print(e)
    return redirect('/shop/checkout')