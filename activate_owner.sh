#!/bin/bash
# سكريبت سريع لتفعيل مستخدم كمالك عقار

echo "🔧 تفعيل مستخدم كمالك عقار"
echo "================================"
echo ""
read -p "أدخل اسم المستخدم (username): " USERNAME

python3 manage.py shell << EOF
from django.contrib.auth.models import User
from accounts.models import UserProfile

try:
    user = User.objects.get(username='$USERNAME')
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.is_owner = True
    profile.save()
    print(f"\n✅ تم تفعيل {user.username} كمالك عقار بنجاح!")
except User.DoesNotExist:
    print(f"\n❌ خطأ: المستخدم '$USERNAME' غير موجود")
except Exception as e:
    print(f"\n❌ خطأ: {e}")
EOF
