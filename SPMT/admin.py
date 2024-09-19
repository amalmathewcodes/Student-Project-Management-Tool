from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'user_type', 'email', 'first_name', 'last_name')  # Add user_type to list_display
    list_filter = ('user_type', 'is_staff', 'is_superuser')  # Add user_type to list_filter

admin.site.register(CustomUser, CustomUserAdmin)
