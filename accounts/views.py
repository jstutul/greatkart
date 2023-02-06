from django.shortcuts import render,redirect,HttpResponse
from accounts.forms import *
from django.contrib import messages,auth
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from carts.views import _cart_id
from carts.models import Cart,CartItem
import requests

def register(request):  # sourcery skip: extract-method
    if request.method == 'POST':
        form=RegistrationsForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split("@")[0]
            
            user=Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number=phone_number
            user.is_active = False
            user.save()
            user.refresh_from_db()
            
            #User activation
            current_site=get_current_site(request)
            mail_subject='Please Active your account'
            message=render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid':  urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request,"Registrations successfull")
            return redirect('/accounts/login?command=verification&email='+str(to_email))
                             
    else:
        form=RegistrationsForm()
    context={
        'form': form,
    }
    return render(request,"accounts/register.html",context)
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)
                    
                    #Getting product varion from cart id
                    product_variation=[]
                    for item in cart_item:
                        variation=item.variations.all()
                        product_variation.append(list(variation))
                    # Get the carts item from the user to access the product variants
                    print(product_variation)
                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id=[]

                    for item in cart_item:
                        existing_variation=item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id) 
                    print(ex_var_list)
                    print(id)
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()
                            
                    # for item in cart_item:
                    #     item.user=user
                    #     item.save()
            except:
                pass 
            auth_login(request, user)
            messages.success(request,"you are now authenticated")
            url=request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query 
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:   
                return redirect('dashboard')
        else:
            messages.error(request, "invalid credential")
            return redirect('login')
    context={}
    return render(request,"accounts/login.html",context)

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Successfully Logout")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        return HttpResponse('Activation link is invalid!')
    
@login_required(login_url='login')     
def dashboard(request):
    return render(request,'accounts/dashboard.html')    

def forgetpassword(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email)
            
            #Reset password
            current_site=get_current_site(request)
            mail_subject='Reset Your Password'
            message=render_to_string('accounts/reset_password_email.html',{
                'user': user,
                'domain': current_site,
                'uid':  urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.error(request,"Password reset email has been sent to your email address")
            return redirect('login')
        else:
            messages.error(request,"Account does not exist")
            return redirect('forgetpassword')     
            
    return render(request,'accounts/forgetpassword.html')    

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid 
        messages.success(request,'Please reset your password.')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link has been expired.')
        return redirect('login')
    

def resetpassword(request):
    if request.method == 'POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        
        if password == confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successfully')
            return redirect('login')
        else:
            messages.error(request,'Password do not match')
            return redirect('resetpassword')
    else:    
        return render(request,'accounts/resetpassword.html')    