# إعداد PythonAnywhere خطوة بخطوة

## 1. التسجيل والدخول
1. اذهب إلى https://www.pythonanywhere.com/
2. اضغط "Create a Beginner account"
3. أكمل التسجيل (لا يطلب بطاقة ائتمانية)

## 2. رفع المشروع
### الطريقة الأولى: عبر Git (موصى به)
```bash
# في PythonAnywhere Console:
git clone https://github.com/yourusername/chalets-main.git
cd chalets-main
```

### الطريقة الثانية: رفع الملفات
1. اذهب إلى Files
2. اضغط "Upload a file"
3. ارفع ملفات المشروع مضغوطة
4. فك الضغط في Console

## 3. إعداد البيئة الافتراضية
```bash
# في Console:
mkvirtualenv --python=/usr/bin/python3.11 chalets-env
workon chalets-env
pip install -r requirements_prod.txt
```

## 4. إعداد قاعدة البيانات
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 5. إعداد Web App
1. اذهب إلى Web > Add a new web app
2. اختر "Manual configuration"
3. اختر Python 3.11
4. في "Virtualenv": /home/yourusername/.virtualenvs/chalets-env
5. في "Code directory": /home/yourusername/chalets-main

## 6. إعدادات WSGI
1. اضغط على "WSGI configuration file"
2. استبدل المحتوى بـ:
```python
import os
import sys

path = '/home/yourusername/chalets-main'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_prod'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 7. متغيرات البيئة
1. اذهب إلى "Variables" في إعدادات Web App
2. أضف:
   - `DJANGO_SETTINGS_MODULE` = `config.settings_prod`
   - `SECRET_KEY` = `your-secret-key-here`

## 8. تشغيل التطبيق
1. اضغط "Reload web app"
2. افتح الرابط: `https://yourusername.pythonanywhere.com`

## ملاحظات هامة:
- الخطة المجانية: 100,000 نقرة/شهر
- التطبيق ينام بعد 5 دقائق عدم نشاط
- يستغرق 30 ثانية للاستيقاظ
- يمكنك رفع ملفات media عبر Files section
