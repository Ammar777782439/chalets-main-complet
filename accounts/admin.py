from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    """إدارة الملف الشخصي داخل صفحة المستخدم"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'
    fields = ('full_name', 'phone_number', 'address', 'is_owner', 'date_of_birth', 'profile_picture')

def get_full_name(obj):
    try:
        return obj.userprofile.full_name
    except UserProfile.DoesNotExist:
        return f"{obj.first_name} {obj.last_name}".strip() or "غير محدد"
get_full_name.short_description = 'الاسم الكامل'

class CustomUserAdmin(UserAdmin):
    """إدارة المستخدمين المخصصة"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', get_full_name, 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'userprofile__full_name', 'email')
    ordering = ('-date_joined',)

# إعادة تسجيل إدارة المستخدم
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """إدارة الملفات الشخصية"""
    list_display = ('user', 'full_name', 'phone_number', 'is_owner', 'date_of_birth')
    list_filter = ('date_of_birth',)
    search_fields = ('user__username', 'full_name', 'phone_number')
    raw_id_fields = ('user',)
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user',)
        }),
        ('المعلومات الشخصية', {
            'fields': ('full_name', 'phone_number', 'address', 'is_owner', 'date_of_birth', 'profile_picture')
        }),
    )
