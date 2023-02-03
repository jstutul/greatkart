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
]