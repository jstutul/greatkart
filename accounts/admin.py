from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User=get_user_model()
admin.site.unregister(Group)

class AccountAdmin(BaseUserAdmin):
    list_display =('email','first_name','last_name','username','last_login','date_joined','is_active')
    filter_horizontal=()
    list_display_links = ('email','first_name','username')
    readonly_fields = ('password',)
    list_filter=()
    fieldsets = ()
    ordering = ('-date_joined',)
admin.site.register(Account,AccountAdmin)