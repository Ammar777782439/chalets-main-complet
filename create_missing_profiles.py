#!/usr/bin/env python3
"""
سكريبت لإنشاء ملفات شخصية للمستخدمين الذين لا يملكون ملفات شخصية
يجب تشغيله من مجلد المشروع الرئيسي
"""

import os
import sys
import django

# إعداد Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile


def create_missing_profiles():
    """إنشاء ملفات شخصية للمستخدمين الذين لا يملكونها"""
    
    print("🔍 البحث عن المستخدمين بدون ملفات شخصية...\n")
    
    users_without_profile = []
    users_with_profile = []
    
    for user in User.objects.all():
        try:
            # محاولة الوصول للملف الشخصي
            profile = user.userprofile
            users_with_profile.append(user)
        except UserProfile.DoesNotExist:
            users_without_profile.append(user)
    
    print(f"📊 الإحصائيات:")
    print(f"   - إجمالي المستخدمين: {User.objects.count()}")
    print(f"   - لديهم ملفات شخصية: {len(users_with_profile)}")
    print(f"   - بدون ملفات شخصية: {len(users_without_profile)}\n")
    
    if not users_without_profile:
        print("✅ جميع المستخدمين لديهم ملفات شخصية!")
        return
    
    print("🔧 إنشاء الملفات الشخصية المفقودة...\n")
    
    created_count = 0
    for user in users_without_profile:
        try:
            profile = UserProfile.objects.create(user=user)
            print(f"   ✅ تم إنشاء ملف شخصي لـ: {user.username}")
            created_count += 1
        except Exception as e:
            print(f"   ❌ فشل إنشاء ملف شخصي لـ {user.username}: {e}")
    
    print(f"\n✨ تم الانتهاء! تم إنشاء {created_count} ملف شخصي جديد")


if __name__ == "__main__":
    create_missing_profiles()
