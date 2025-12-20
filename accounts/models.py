from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    """نموذج الملف الشخصي الموسع للمستخدم"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    full_name = models.CharField(max_length=100, blank=True, verbose_name="الاسم الرباعي")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="رقم الهاتف")
    address = models.TextField(blank=True, verbose_name="العنوان")
    is_owner = models.BooleanField(default=False, verbose_name="مالك؟", help_text="يحدد ما إذا كان للمستخدم صلاحية المالك للوصول إلى لوحة المالك.")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="تاريخ الميلاد")
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True, 
        verbose_name="صورة الملف الشخصي"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """التحقق من أن الاسم الكامل يحتوي على أربعة أسماء"""
        from django.core.exceptions import ValidationError
        if self.full_name:
            names = self.full_name.strip().split()
            if len(names) < 4:
                raise ValidationError({'full_name': 'يجب إدخال الاسم الرباعي (أربعة أسماء على الأقل)'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "الملف الشخصي"
        verbose_name_plural = "الملفات الشخصية"

    def __str__(self):
        return f"ملف {self.user.get_full_name() or self.user.username}"

    def get_absolute_url(self):
        return reverse('accounts:profile')
