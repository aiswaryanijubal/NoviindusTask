from django.contrib import admin
from tma.models import CustomUser,Task,AdminManage
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms


class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    model = CustomUser
    list_display = ('username', 'name', 'user_type', 'is_staff')
    search_fields = ('username', 'name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': ('name', 'phone_number', 'address', 'user_type')
        }),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'name', 'password1', 'password2',
                'user_type', 
                'is_staff', 'is_active', 'is_superuser'
            )}
        ),
    )
    
    
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task)
admin.site.register(AdminManage)
