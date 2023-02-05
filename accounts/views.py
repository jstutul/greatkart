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
            auth_login(request, user)
            messages.success(request,"you are now authenticated")
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