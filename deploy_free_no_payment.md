# نشر مجاني بدون طريقة دفع

## 1. PythonAnywhere (الأفضل بدون دفع)
### المميزات:
- خطة مجانية كاملة
- لا يطلب طريقة دفع
- يدعم Django مباشرة
- نقرات في الساعة: 100,000

### خطوات النشر:
```bash
# 1. سجل في https://www.pythonanywhere.com/
# 2. اذهب إلى Dashboard > Web > Add a new web app
# 3. اختر Django و Python 3.11
# 4. ارفع ملفات المشروع عبر Git أو الملفات
# 5. في VirtualEnv: pip install -r requirements_prod.txt
# 6. عدّل WSGI configuration
# 7. شغّل migrate و collectstatic
```

## 2. Render.com (بدون دفع للخطة الأساسية)
### المميزات:
- 750 ساعة/شهر مجانية
- نشر تلقائي من GitHub
- PostgreSQL مجاني
- لا يطلب بطاقة للخطة المجانية

### خطوات النشر:
```bash
# 1. سجل في https://render.com/
# 2. ربط حساب GitHub
# 3. New > Web Service
# 4. اختر repo المشروع
# 5. Build Command: pip install -r requirements_prod.txt && python manage.py collectstatic --noinput
# 6. Start Command: gunicorn config.wsgi:application
# 7. Environment Variables: DJANGO_SETTINGS_MODULE=config.settings_prod
```

## 3. Vercel (لـ Django API)
### المميزات:
- 100GB bandwidth مجانية
- نشر فوري
- SSL مجاني
- لا يطلب دفع للخطة المجانية

### خطوات النشر:
```bash
# 1. سجل في https://vercel.com/
# 2. تثبيت Vercel CLI: npm i -g vercel
# 3. في مجلد المشروع: vercel
# 4. اتبع التعليمات
# 5. vercel --prod للنشر النهائي
```

## 4. Glitch (للمشاريع الصغيرة)
### المميزات:
- 1000 ساعة/شهر مجانية
- محرر عبر الإنترنت
- لا يحتاج بطاقة ائتمانية
- مناسب للمشاريع التجريبية

### خطوات النشر:
```bash
# 1. اذهب إلى https://glitch.com/
# 2. New Project > Import from GitHub
# 3. أضف رابط repo المشروع
# 4. عدّل package.json إذا لزم الأمر
# 5. شغّل المشروع
```

## التوصية:
**PythonAnywhere** هو الخيار الأفضل لمشروع Django بدون طريقة دفع، لأنه:
- مصمم خصيصاً لـ Python/Django
- واجهة سهلة للمبتدئين
- مستقر وموثوق
- لا يطلب معلومات دفع أبداً
