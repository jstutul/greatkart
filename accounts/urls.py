from django.urls import path
from .import views
urlpatterns = [
   path('register',views.register,name='register'),
   path('login',views.login,name='login'),
   path('logout',views.logout,name='logout'),
   path('dashboard/',views.dashboard,name='dashboard'),
   path('',views.dashboard,name='dashboard'),
   path('activate/(<uidb64>[0-9A-Za-z_\-]+)/(<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
      views.activate, name='activate'),
   path('forgetpassword',views.forgetpassword,name="forgetpassword"),
   path('resetpassword_validate/(<uidb64>[0-9A-Za-z_\-]+)/(<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
      views.resetpassword_validate, name='resetpassword_validate'),
   path('resetpassword',views.resetpassword,name="resetpassword"),
]