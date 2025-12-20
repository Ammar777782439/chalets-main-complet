#!/usr/bin/env python
"""
سكربت اختبار شامل لجميع API endpoints
"""
import requests
from datetime import datetime, timedelta
import json

BASE_URL = "http://127.0.0.1:8000/api"

# ألوان للطباعة
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed, response=None):
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} - {name}")
    if not passed and response:
        print(f"      Status: {response.status_code}")
        try:
            print(f"      Response: {response.json()}")
        except:
            print(f"      Response: {response.text[:200]}")

def print_section(name):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}")
    print(f" {name}")
    print(f"{'='*50}{Colors.RESET}")

results = {"passed": 0, "failed": 0}

def test(name, condition, response=None):
    global results
    if condition:
        results["passed"] += 1
    else:
        results["failed"] += 1
    print_test(name, condition, response)
    return condition

# ============================================
# 1. اختبار المصادقة
# ============================================
print_section("1. اختبارات المصادقة (Authentication)")

# تسجيل مستخدم جديد
username = f"test_user_{datetime.now().strftime('%H%M%S')}"
register_data = {
    "username": username,
    "email": f"{username}@example.com",
    "password": "TestPass123!",
    "full_name": "أحمد محمد علي الخالدي",
    "phone_number": "966501234567"
}
response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
test("تسجيل مستخدم جديد", response.status_code == 201, response)

# تسجيل الدخول
login_data = {"username": username, "password": "TestPass123!"}
response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
login_success = response.status_code == 200 and 'access' in response.json()
test("تسجيل الدخول", login_success, response)

access_token = None
refresh_token = None
if login_success:
    tokens = response.json()
    access_token = tokens['access']
    refresh_token = tokens['refresh']

headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

# تحديث التوكن
if refresh_token:
    response = requests.post(f"{BASE_URL}/auth/refresh/", json={"refresh": refresh_token})
    test("تحديث التوكن (Refresh)", response.status_code == 200 and 'access' in response.json(), response)

# ============================================
# 2. اختبار الملف الشخصي
# ============================================
print_section("2. اختبارات الملف الشخصي (User Profile)")

# عرض الملف الشخصي
response = requests.get(f"{BASE_URL}/user/profile/", headers=headers)
test("عرض الملف الشخصي", response.status_code == 200, response)

# تحديث الملف الشخصي
update_data = {
    "full_name": "أحمد محمد علي السعيد",
    "phone_number": "966509876543",
    "address": "الرياض"
}
response = requests.patch(f"{BASE_URL}/user/profile/", json=update_data, headers=headers)
test("تحديث الملف الشخصي", response.status_code == 200, response)

# تغيير كلمة المرور
password_data = {"old_password": "TestPass123!", "new_password": "NewPass456!"}
response = requests.post(f"{BASE_URL}/user/password-change/", json=password_data, headers=headers)
test("تغيير كلمة المرور", response.status_code == 200, response)

# ============================================
# 3. اختبار العقارات
# ============================================
print_section("3. اختبارات العقارات (Properties)")

# قائمة العقارات
response = requests.get(f"{BASE_URL}/properties/")
test("قائمة العقارات", response.status_code == 200 and 'results' in response.json(), response)
properties = response.json().get('results', [])

# فلترة بالمدينة
response = requests.get(f"{BASE_URL}/properties/", params={"city": "Riyadh"})
test("فلترة العقارات بالمدينة", response.status_code == 200, response)

# فلترة بالسعر
response = requests.get(f"{BASE_URL}/properties/", params={"min_price": 100, "max_price": 500})
test("فلترة العقارات بالسعر", response.status_code == 200, response)

# بحث
response = requests.get(f"{BASE_URL}/properties/", params={"search": "شاليه"})
test("بحث في العقارات", response.status_code == 200, response)

# ترتيب
response = requests.get(f"{BASE_URL}/properties/", params={"ordering": "-price_per_day"})
test("ترتيب العقارات بالسعر", response.status_code == 200, response)

# تفاصيل عقار
if properties:
    prop_id = properties[0]['id']
    response = requests.get(f"{BASE_URL}/properties/{prop_id}/")
    test(f"تفاصيل العقار (ID={prop_id})", response.status_code == 200, response)
    
    # معرض الصور
    response = requests.get(f"{BASE_URL}/properties/{prop_id}/gallery/")
    test(f"معرض صور العقار (ID={prop_id})", response.status_code == 200, response)

# عقار غير موجود
response = requests.get(f"{BASE_URL}/properties/99999/")
test("عقار غير موجود (404)", response.status_code == 404, response)

# ============================================
# 4. اختبار المرافق
# ============================================
print_section("4. اختبارات المرافق (Amenities)")

response = requests.get(f"{BASE_URL}/amenities/")
test("قائمة المرافق", response.status_code == 200, response)

# ============================================
# 5. اختبار التقييمات
# ============================================
print_section("5. اختبارات التقييمات (Reviews)")

# قائمة التقييمات
response = requests.get(f"{BASE_URL}/reviews/")
test("قائمة التقييمات", response.status_code == 200, response)

# إضافة تقييم
if properties:
    review_data = {
        "property": properties[0]['id'],
        "rating": 5,
        "comment": "تجربة رائعة جداً! اختبار تلقائي."
    }
    response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=headers)
    test("إضافة تقييم جديد", response.status_code == 201, response)

# ============================================
# 6. اختبار الحجوزات
# ============================================
print_section("6. اختبارات الحجوزات (Bookings)")

# قائمة الحجوزات
response = requests.get(f"{BASE_URL}/bookings/", headers=headers)
test("قائمة حجوزاتي", response.status_code == 200, response)

booking_id = None
if properties:
    # التحقق من التوفر
    start = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
    end = (datetime.now() + timedelta(days=31)).isoformat() + "Z"
    
    availability_data = {
        "property_id": properties[0]['id'],
        "start_datetime": start,
        "end_datetime": end
    }
    response = requests.post(f"{BASE_URL}/bookings/check-availability/", json=availability_data, headers=headers)
    test("التحقق من توفر العقار", response.status_code == 200, response)
    
    # إنشاء حجز
    booking_data = {
        "property": properties[0]['id'],
        "start_datetime": start,
        "end_datetime": end,
        "booking_type": "full_day",
        "customer_name": "أحمد محمد علي الخالدي",
        "customer_phone": "966501234567"
    }
    response = requests.post(f"{BASE_URL}/bookings/", json=booking_data, headers=headers)
    test("إنشاء حجز جديد", response.status_code == 201, response)
    
    if response.status_code == 201:
        booking_id = response.json().get('id')
        
        # تفاصيل الحجز
        response = requests.get(f"{BASE_URL}/bookings/{booking_id}/", headers=headers)
        test(f"تفاصيل الحجز (ID={booking_id})", response.status_code == 200, response)
        
        # إلغاء الحجز
        response = requests.post(f"{BASE_URL}/bookings/{booking_id}/cancel/", headers=headers)
        test(f"إلغاء الحجز (ID={booking_id})", response.status_code == 200, response)

# ============================================
# 7. اختبار المدفوعات
# ============================================
print_section("7. اختبارات المدفوعات (Payments)")

# قائمة وسائل الدفع
response = requests.get(f"{BASE_URL}/payments/providers/")
test("قائمة وسائل الدفع", response.status_code == 200, response)

# ============================================
# 8. اختبار تسجيل الخروج
# ============================================
print_section("8. اختبار تسجيل الخروج (Logout)")

if refresh_token:
    # نحتاج تسجيل دخول جديد لأننا غيرنا كلمة المرور
    login_data = {"username": username, "password": "NewPass456!"}
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        new_tokens = response.json()
        new_access = new_tokens['access']
        new_refresh = new_tokens['refresh']
        new_headers = {"Authorization": f"Bearer {new_access}"}
        
        response = requests.post(f"{BASE_URL}/auth/logout/", json={"refresh": new_refresh}, headers=new_headers)
        test("تسجيل الخروج", response.status_code == 205, response)

# ============================================
# النتائج النهائية
# ============================================
print(f"\n{Colors.BOLD}{'='*50}")
print(f" النتائج النهائية")
print(f"{'='*50}{Colors.RESET}")
total = results["passed"] + results["failed"]
print(f"  {Colors.GREEN}✓ نجح: {results['passed']}{Colors.RESET}")
print(f"  {Colors.RED}✗ فشل: {results['failed']}{Colors.RESET}")
print(f"  الإجمالي: {total}")
print(f"  النسبة: {(results['passed']/total*100):.1f}%" if total > 0 else "")
print(f"{'='*50}\n")
