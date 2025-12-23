# خطوات نشر مشروع Chalets على Heroku مجاناً

## 1. التحضير
```bash
# تثبيت Heroku CLI
# إنشاء حساب على https://signup.heroku.com/

# تسجيل الدخول
heroku login
```

## 2. إعداد المشروع
```bash
# إنشاء تطبيق جديد
heroku create your-unique-app-name

# إضافة PostgreSQL مجاني
heroku addons:create heroku-postgresql:essential-0

# إعداد متغيرات البيئة
heroku config:set SECRET_KEY='your-very-secret-key-here'
heroku config:set DJANGO_SETTINGS_MODULE=config.settings_prod
```

## 3. النشر
```bash
# إضافة ملفات الإنتاج إلى Git
git add .
git commit -m "Ready for production deployment"

# الدفع إلى Heroku
git push heroku main

# تشغيل الترحيل
heroku run python manage.py migrate

# جمع الملفات الثابتة
heroku run python manage.py collectstatic --noinput

# إنشاء مستخدم مدير
heroku run python manage.py createsuperuser
```

## 4. فتح التطبيق
```bash
heroku open
```

## ملاحظات هامة:
- الخطة المجانية Heroku لها حدود: 550 ساعة/شهر
- PostgreSQL مجاني يصل إلى 10,000 صف
- التطبيق ي睡眠 بعد 30 دقيقة عدم نشاط
- يمكن إضافة بطاقة ائتمان للحدود الأعلى (بدون تكلفة)
