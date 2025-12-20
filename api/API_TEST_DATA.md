# بيانات اختبار API - منصة حجز العقارات

> **ملاحظة:** استبدل `BASE_URL` بعنوان السيرفر الخاص بك (مثال: `http://127.0.0.1:8000/api`)
> واستبدل `ACCESS_TOKEN` بالتوكن الذي تحصل عليه من تسجيل الدخول

---

## 1. المصادقة (Authentication)

### 1.1 تسجيل مستخدم جديد (Register)

**Endpoint:** `POST /api/auth/register/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "username": "ahmed_user",
    "email": "ahmed@example.com",
    "password": "SecurePass123!",
    "full_name": "أحمد محمد علي الخالدي",
    "phone_number": "966501234567"
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ahmed_user",
    "email": "ahmed@example.com",
    "password": "SecurePass123!",
    "full_name": "أحمد محمد علي الخالدي",
    "phone_number": "966501234567"
  }'
```

**Python (requests):**
```python
import requests

url = "http://127.0.0.1:8000/api/auth/register/"
data = {
    "username": "ahmed_user",
    "email": "ahmed@example.com",
    "password": "SecurePass123!",
    "full_name": "أحمد محمد علي الخالدي",
    "phone_number": "966501234567"
}
response = requests.post(url, json=data)
print(response.json())
```

**Response المتوقعة (201 Created):**
```json
{
    "id": 1,
    "username": "ahmed_user",
    "email": "ahmed@example.com"
}
```

---

### 1.2 تسجيل الدخول (Login)

**Endpoint:** `POST /api/auth/login/`

**Body (JSON):**
```json
{
    "username": "ahmed_user",
    "password": "SecurePass123!"
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ahmed_user",
    "password": "SecurePass123!"
  }'
```


**Response المتوقعة (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 1.3 تحديث التوكن (Refresh Token)

**Endpoint:** `POST /api/auth/refresh/`

**Body (JSON):**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/refresh/" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

**Response المتوقعة (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 1.4 تسجيل الخروج (Logout)

**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "refresh": "YOUR_REFRESH_TOKEN"
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/logout/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

**Response المتوقعة (205 Reset Content):**
*فارغة*

---

## 2. ملف المستخدم (User Profile)

### 2.1 عرض الملف الشخصي (Get Profile)

**Endpoint:** `GET /api/user/profile/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
```

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/user/profile/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Python (requests):**
```python
import requests

url = "http://127.0.0.1:8000/api/user/profile/"
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(url, headers=headers)
print(response.json())
```

**Response المتوقعة (200 OK):**
```json
{
    "full_name": "أحمد محمد علي الخالدي",
    "phone_number": "966501234567",
    "address": null,
    "date_of_birth": null,
    "profile_picture": null,
    "username": "ahmed_user",
    "email": "ahmed@example.com"
}
```

---

### 2.2 تحديث الملف الشخصي (Update Profile)

**Endpoint:** `PATCH /api/user/profile/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "full_name": "أحمد محمد علي الخالدي",
    "phone_number": "966509876543",
    "address": "الرياض، حي النخيل، شارع الأمير سلطان",
    "date_of_birth": "1990-05-15"
}
```

**cURL:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/user/profile/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "أحمد محمد علي الخالدي",
    "phone_number": "966509876543",
    "address": "الرياض، حي النخيل، شارع الأمير سلطان",
    "date_of_birth": "1990-05-15"
  }'
```

**Response المتوقعة (200 OK):**
```json
{
    "full_name": "أحمد محمد علي الخالدي",
    "phone_number": "966509876543",
    "address": "الرياض، حي النخيل، شارع الأمير سلطان",
    "date_of_birth": "1990-05-15",
    "profile_picture": null,
    "username": "ahmed_user",
    "email": "ahmed@example.com"
}
```

---

### 2.3 تغيير كلمة المرور (Change Password)

**Endpoint:** `POST /api/user/password-change/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass456!"
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/user/password-change/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass456!"
  }'
```

**Response المتوقعة (200 OK):**
```json
{
    "status": "تم تغيير كلمة المرور بنجاح"
}
```

---

### 2.4 حذف الحساب (Delete Account)

**Endpoint:** `DELETE /api/user/delete-account/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
```

**cURL:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/user/delete-account/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response المتوقعة (204 No Content):**
*فارغة*

---

## 3. العقارات (Properties)

### 3.1 قائمة العقارات (List Properties)

**Endpoint:** `GET /api/properties/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/properties/"
```

**Response المتوقعة (200 OK):**
```json
{
    "count": 10,
    "next": "http://127.0.0.1:8000/api/properties/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "شاليه الأحلام",
            "description": "شاليه فاخر مع مسبح خاص",
            "city": "جدة",
            "price_per_day": 500.00,
            "main_image": "http://127.0.0.1:8000/media/properties/chalet1.jpg",
            "property_type": "chalet",
            "capacity": 10,
            "amenities": [
                {"id": 1, "name": "مسبح", "icon": "🏊"},
                {"id": 2, "name": "واي فاي", "icon": "📶"}
            ],
            "is_verified_by_platform": true,
            "privacy_rating": 5
        }
    ]
}
```

---

### 3.2 فلترة العقارات (Filter Properties)

**Endpoint:** `GET /api/properties/?city=Riyadh&min_price=100&max_price=500`

**Parameters المتاحة:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `city` | string | اسم المدينة |
| `min_price` | number | الحد الأدنى للسعر |
| `max_price` | number | الحد الأعلى للسعر |
| `capacity` | number | السعة المطلوبة |
| `property_type` | string | نوع العقار (chalet, garden, istiraha) |
| `is_verified_by_platform` | boolean | موثق من المنصة |
| `search` | string | بحث في الاسم والوصف والمدينة |
| `ordering` | string | ترتيب (price_per_day, -price_per_day, created_at, -created_at) |
| `page` | number | رقم الصفحة |
| `page_size` | number | عدد النتائج في الصفحة |

**cURL Examples:**

```bash
# فلترة بالمدينة والسعر
curl -X GET "http://127.0.0.1:8000/api/properties/?city=Riyadh&min_price=100&max_price=500"

# بحث في العقارات
curl -X GET "http://127.0.0.1:8000/api/properties/?search=شاليه"

# ترتيب بالسعر تصاعدياً
curl -X GET "http://127.0.0.1:8000/api/properties/?ordering=price_per_day"

# ترتيب بالسعر تنازلياً
curl -X GET "http://127.0.0.1:8000/api/properties/?ordering=-price_per_day"

# فلترة متقدمة
curl -X GET "http://127.0.0.1:8000/api/properties/?city=Jeddah&min_price=200&property_type=chalet&is_verified_by_platform=true&ordering=-price_per_day"
```

**Python (requests):**
```python
import requests

url = "http://127.0.0.1:8000/api/properties/"
params = {
    "city": "Riyadh",
    "min_price": 100,
    "max_price": 500,
    "property_type": "chalet",
    "is_verified_by_platform": True,
    "ordering": "-price_per_day",
    "page": 1,
    "page_size": 10
}
response = requests.get(url, params=params)
print(response.json())
```

---

### 3.3 تفاصيل عقار (Property Detail)

**Endpoint:** `GET /api/properties/{id}/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/properties/1/"
```

**Response المتوقعة (200 OK):**
```json
{
    "id": 1,
    "name": "شاليه الأحلام",
    "description": "شاليه فاخر مع مسبح خاص وحديقة واسعة",
    "city": "جدة",
    "address": "طريق الكورنيش",
    "price_per_day": 500.00,
    "price_half_day": 300.00,
    "price_per_hour": 100.00,
    "main_image": "http://127.0.0.1:8000/media/properties/chalet1.jpg",
    "property_type": "chalet",
    "capacity": 10,
    "amenities": [
        {"id": 1, "name": "مسبح", "icon": "🏊"},
        {"id": 2, "name": "واي فاي", "icon": "📶"},
        {"id": 3, "name": "شواء", "icon": "🍖"}
    ],
    "gallery_images": [
        {"id": 1, "image": "/media/gallery/img1.jpg", "image_url": "http://...", "caption": "المسبح"},
        {"id": 2, "image": "/media/gallery/img2.jpg", "image_url": "http://...", "caption": "الحديقة"}
    ],
    "is_verified_by_platform": true,
    "privacy_rating": 5,
    "owner_name": "محمد الأحمد",
    "reviews_avg": 4.5,
    "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 3.4 معرض صور العقار (Property Gallery)

**Endpoint:** `GET /api/properties/{id}/gallery/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/properties/1/gallery/"
```

**Response المتوقعة (200 OK):**
```json
[
    {
        "id": 1,
        "image": "/media/gallery/img1.jpg",
        "image_url": "http://127.0.0.1:8000/media/gallery/img1.jpg",
        "caption": "المسبح الخارجي"
    },
    {
        "id": 2,
        "image": "/media/gallery/img2.jpg",
        "image_url": "http://127.0.0.1:8000/media/gallery/img2.jpg",
        "caption": "غرفة المعيشة"
    }
]
```

---

### 3.5 بحث العقارات (Search Properties)

**Endpoint:** `GET /api/properties/search/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/properties/search/?search=شاليه&city=Jeddah"
```

---

## 4. المرافق (Amenities)

### 4.1 قائمة المرافق (List Amenities)

**Endpoint:** `GET /api/amenities/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/amenities/"
```

**Response المتوقعة (200 OK):**
```json
[
    {"id": 1, "name": "مسبح", "icon": "🏊"},
    {"id": 2, "name": "واي فاي", "icon": "📶"},
    {"id": 3, "name": "شواء", "icon": "🍖"},
    {"id": 4, "name": "مواقف سيارات", "icon": "🚗"},
    {"id": 5, "name": "تكييف", "icon": "❄️"},
    {"id": 6, "name": "ملعب أطفال", "icon": "🎢"}
]
```

---

## 5. التقييمات (Reviews)

### 5.1 قائمة التقييمات (List Reviews)

**Endpoint:** `GET /api/reviews/`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `property` | number | ID العقار للفلترة |

**cURL:**
```bash
# جميع التقييمات
curl -X GET "http://127.0.0.1:8000/api/reviews/"

# تقييمات عقار محدد
curl -X GET "http://127.0.0.1:8000/api/reviews/?property=1"
```

**Response المتوقعة (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "property": 1,
            "user": 2,
            "user_name": "خالد السعود",
            "rating": 5,
            "comment": "تجربة رائعة! المكان نظيف والخدمة ممتازة",
            "created_at": "2024-01-20T14:30:00Z"
        }
    ]
}
```

---

### 5.2 إضافة تقييم (Create Review)

**Endpoint:** `POST /api/reviews/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "property": 1,
    "rating": 5,
    "comment": "تجربة رائعة جداً! الشاليه نظيف والمسبح ممتاز. أنصح به بشدة."
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/reviews/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property": 1,
    "rating": 5,
    "comment": "تجربة رائعة جداً! الشاليه نظيف والمسبح ممتاز. أنصح به بشدة."
  }'
```

**Python (requests):**
```python
import requests

url = "http://127.0.0.1:8000/api/reviews/"
headers = {"Authorization": f"Bearer {access_token}"}
data = {
    "property": 1,
    "rating": 5,
    "comment": "تجربة رائعة جداً!"
}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

**Response المتوقعة (201 Created):**
```json
{
    "id": 6,
    "property": 1,
    "user": 3,
    "user_name": "أحمد محمد علي الخالدي",
    "rating": 5,
    "comment": "تجربة رائعة جداً! الشاليه نظيف والمسبح ممتاز. أنصح به بشدة.",
    "created_at": "2024-12-20T15:00:00Z"
}
```

---

## 6. الحجوزات (Bookings)

### 6.1 قائمة حجوزاتي (My Bookings)

**Endpoint:** `GET /api/bookings/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
```

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/bookings/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response المتوقعة (200 OK):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "property": 1,
            "property_name": "شاليه الأحلام",
            "start_datetime": "2024-12-25T14:00:00Z",
            "end_datetime": "2024-12-26T12:00:00Z",
            "booking_type": "full_day",
            "customer_name": "أحمد محمد علي الخالدي",
            "customer_phone": "966501234567",
            "total_price": 500.00,
            "status": "pending",
            "payment_status": "unpaid",
            "deposit_amount": 100.00,
            "guests": [],
            "created_at": "2024-12-20T10:00:00Z"
        }
    ]
}
```

---

### 6.2 إنشاء حجز جديد (Create Booking)

**Endpoint:** `POST /api/bookings/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON) - حجز يوم كامل:**
```json
{
    "property": 1,
    "start_datetime": "2024-12-25T14:00:00Z",
    "end_datetime": "2024-12-26T12:00:00Z",
    "booking_type": "full_day",
    "customer_name": "أحمد محمد علي الخالدي",
    "customer_phone": "966501234567",
    "guest_names": "محمد أحمد\nعلي سعيد\nخالد فهد"
}
```

**Body (JSON) - حجز بالساعة:**
```json
{
    "property": 1,
    "start_datetime": "2024-12-25T10:00:00Z",
    "end_datetime": "2024-12-25T14:00:00Z",
    "booking_type": "hourly",
    "customer_name": "أحمد محمد علي الخالدي",
    "customer_phone": "966501234567"
}
```

**Body (JSON) - حجز نصف يوم:**
```json
{
    "property": 1,
    "start_datetime": "2024-12-25T14:00:00Z",
    "end_datetime": "2024-12-25T20:00:00Z",
    "booking_type": "half_day",
    "customer_name": "أحمد محمد علي الخالدي",
    "customer_phone": "966501234567"
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/bookings/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property": 1,
    "start_datetime": "2024-12-25T14:00:00Z",
    "end_datetime": "2024-12-26T12:00:00Z",
    "booking_type": "full_day",
    "customer_name": "أحمد محمد علي الخالدي",
    "customer_phone": "966501234567",
    "guest_names": "محمد أحمد\nعلي سعيد\nخالد فهد"
  }'
```

**Python (requests):**
```python
import requests
from datetime import datetime, timedelta

url = "http://127.0.0.1:8000/api/bookings/"
headers = {"Authorization": f"Bearer {access_token}"}

start = (datetime.now() + timedelta(days=5)).isoformat() + "Z"
end = (datetime.now() + timedelta(days=6)).isoformat() + "Z"

data = {
    "property": 1,
    "start_datetime": start,
    "end_datetime": end,
    "booking_type": "full_day",
    "customer_name": "أحمد محمد علي الخالدي",
    "customer_phone": "966501234567",
    "guest_names": "محمد أحمد\nعلي سعيد"
}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

**Response المتوقعة (201 Created):**
```json
{
    "id": 5,
    "property": 1,
    "property_name": "شاليه الأحلام",
    "start_datetime": "2024-12-25T14:00:00Z",
    "end_datetime": "2024-12-26T12:00:00Z",
    "booking_type": "full_day",
    "customer_name": "أحمد محمد علي الخالدي",
    "customer_phone": "966501234567",
    "total_price": 500.00,
    "status": "pending",
    "payment_status": "unpaid",
    "deposit_amount": 100.00,
    "guests": [
        {"id": 1, "serial": 1, "name": "محمد أحمد", "code": "ABC123"},
        {"id": 2, "serial": 2, "name": "علي سعيد", "code": "DEF456"},
        {"id": 3, "serial": 3, "name": "خالد فهد", "code": "GHI789"}
    ],
    "created_at": "2024-12-20T15:00:00Z"
}
```

---

### 6.3 تفاصيل حجز (Booking Detail)

**Endpoint:** `GET /api/bookings/{id}/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
```

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/bookings/1/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 6.4 إلغاء حجز (Cancel Booking) - الطريقة الأولى

**Endpoint:** `POST /api/bookings/{id}/cancel/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/bookings/1/cancel/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response المتوقعة (200 OK):**
```json
{
    "status": "تم إلغاء الحجز"
}
```

---

### 6.5 إلغاء حجز (Cancel Booking) - الطريقة الثانية

**Endpoint:** `POST /api/bookings/cancel/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "booking_id": 1
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/bookings/cancel/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"booking_id": 1}'
```

---

### 6.6 التحقق من توفر العقار (Check Availability)

**Endpoint:** `POST /api/bookings/check-availability/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "property_id": 1,
    "start_datetime": "2024-12-25T14:00:00Z",
    "end_datetime": "2024-12-26T12:00:00Z"
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/bookings/check-availability/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 1,
    "start_datetime": "2024-12-25T14:00:00Z",
    "end_datetime": "2024-12-26T12:00:00Z"
  }'
```

**Python (requests):**
```python
import requests

url = "http://127.0.0.1:8000/api/bookings/check-availability/"
headers = {"Authorization": f"Bearer {access_token}"}
data = {
    "property_id": 1,
    "start_datetime": "2024-12-25T14:00:00Z",
    "end_datetime": "2024-12-26T12:00:00Z"
}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

**Response المتوقعة (200 OK):**
```json
{
    "available": true
}
```

**أو إذا كان محجوزاً:**
```json
{
    "available": false
}
```

---

## 7. المدفوعات (Payments)

### 7.1 قائمة وسائل الدفع (Payment Providers)

**Endpoint:** `GET /api/payments/providers/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/payments/providers/"
```

**Response المتوقعة (200 OK):**
```json
[
    {
        "id": 1,
        "name": "الراجحي",
        "account_number": "SA1234567890123456789012",
        "provider_type": "bank",
        "icon": "/media/providers/rajhi.png",
        "icon_url": "http://127.0.0.1:8000/media/providers/rajhi.png"
    },
    {
        "id": 2,
        "name": "STC Pay",
        "account_number": "0501234567",
        "provider_type": "wallet",
        "icon": "/media/providers/stc.png",
        "icon_url": "http://127.0.0.1:8000/media/providers/stc.png"
    }
]
```

---

### 7.2 تقديم دفعة (Submit Payment)

**Endpoint:** `POST /api/payments/submit/`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "booking": 1,
    "payment_method": "bank_transfer",
    "provider": 1,
    "transaction_id": "TX202412200001",
    "payer_full_name": "أحمد محمد علي الخالدي",
    "amount": 500.00
}
```

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/payments/submit/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking": 1,
    "payment_method": "bank_transfer",
    "provider": 1,
    "transaction_id": "TX202412200001",
    "payer_full_name": "أحمد محمد علي الخالدي",
    "amount": 500.00
  }'
```

**Python (requests):**
```python
import requests

url = "http://127.0.0.1:8000/api/payments/submit/"
headers = {"Authorization": f"Bearer {access_token}"}
data = {
    "booking": 1,
    "payment_method": "bank_transfer",
    "provider": 1,
    "transaction_id": "TX202412200001",
    "payer_full_name": "أحمد محمد علي الخالدي",
    "amount": 500.00
}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

**Response المتوقعة (201 Created):**
```json
{
    "id": 1,
    "booking": 1,
    "payment_method": "bank_transfer",
    "provider": 1,
    "transaction_id": "TX202412200001",
    "payer_full_name": "أحمد محمد علي الخالدي",
    "amount": 500.00,
    "status": "pending",
    "is_valid": false,
    "created_at": "2024-12-20T15:30:00Z"
}
```

---

### 7.3 حالة الدفع (Payment Status)

**Endpoint:** `GET /api/payments/status/?booking_id=1`

**Headers:**
```
Authorization: Bearer ACCESS_TOKEN
```

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/payments/status/?booking_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response المتوقعة (200 OK):**
```json
{
    "id": 1,
    "booking": 1,
    "payment_method": "bank_transfer",
    "provider": 1,
    "transaction_id": "TX202412200001",
    "payer_full_name": "أحمد محمد علي الخالدي",
    "amount": 500.00,
    "status": "confirmed",
    "is_valid": true,
    "created_at": "2024-12-20T15:30:00Z"
}
```

---

## 8. أكواد الخطأ الشائعة (Common Error Codes)

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | بيانات غير صحيحة |
| 401 | Unauthorized | غير مصرح - التوكن غير صالح أو منتهي |
| 403 | Forbidden | ممنوع - لا تملك الصلاحية |
| 404 | Not Found | غير موجود |
| 409 | Conflict | تعارض - مثل محاولة حجز وقت محجوز |

**أمثلة على رسائل الخطأ:**

**خطأ في التسجيل (اسم رباعي):**
```json
{
    "full_name": ["يجب إدخال الاسم الرباعي (أربعة أسماء على الأقل)"]
}
```

**خطأ في الحجز (تعارض أوقات):**
```json
{
    "non_field_errors": ["عذراً، هذا العقار محجوز بالفعل في الفترة الزمنية المحددة. يرجى اختيار وقت آخر."]
}
```

**خطأ في تغيير كلمة المرور:**
```json
{
    "old_password": ["كلمة المرور القديمة غير صحيحة"]
}
```

---

## 9. سيناريو اختبار كامل (Full Test Scenario)

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

# 1. تسجيل مستخدم جديد
print("=== تسجيل مستخدم ===")
register_data = {
    "username": "test_user_2024",
    "email": "test2024@example.com",
    "password": "TestPass123!",
    "full_name": "محمد أحمد علي السالم",
    "phone_number": "966501234567"
}
response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# 2. تسجيل الدخول
print("\n=== تسجيل الدخول ===")
login_data = {
    "username": "test_user_2024",
    "password": "TestPass123!"
}
response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
tokens = response.json()
access_token = tokens.get('access')
refresh_token = tokens.get('refresh')
print(f"Access Token: {access_token[:50]}...")

headers = {"Authorization": f"Bearer {access_token}"}

# 3. عرض الملف الشخصي
print("\n=== الملف الشخصي ===")
response = requests.get(f"{BASE_URL}/user/profile/", headers=headers)
print(f"Profile: {response.json()}")

# 4. قائمة العقارات
print("\n=== قائمة العقارات ===")
response = requests.get(f"{BASE_URL}/properties/")
properties = response.json()
print(f"Total Properties: {properties.get('count', 0)}")

if properties.get('results'):
    property_id = properties['results'][0]['id']
    
    # 5. تفاصيل عقار
    print(f"\n=== تفاصيل العقار {property_id} ===")
    response = requests.get(f"{BASE_URL}/properties/{property_id}/")
    print(f"Property: {response.json()}")
    
    # 6. التحقق من التوفر
    print("\n=== التحقق من التوفر ===")
    start = (datetime.now() + timedelta(days=10)).isoformat() + "Z"
    end = (datetime.now() + timedelta(days=11)).isoformat() + "Z"
    availability_data = {
        "property_id": property_id,
        "start_datetime": start,
        "end_datetime": end
    }
    response = requests.post(
        f"{BASE_URL}/bookings/check-availability/",
        json=availability_data,
        headers=headers
    )
    print(f"Availability: {response.json()}")
    
    # 7. إنشاء حجز
    if response.json().get('available'):
        print("\n=== إنشاء حجز ===")
        booking_data = {
            "property": property_id,
            "start_datetime": start,
            "end_datetime": end,
            "booking_type": "full_day",
            "customer_name": "محمد أحمد علي السالم",
            "customer_phone": "966501234567"
        }
        response = requests.post(
            f"{BASE_URL}/bookings/",
            json=booking_data,
            headers=headers
        )
        print(f"Booking: {response.json()}")

# 8. تسجيل الخروج
print("\n=== تسجيل الخروج ===")
logout_data = {"refresh": refresh_token}
response = requests.post(
    f"{BASE_URL}/auth/logout/",
    json=logout_data,
    headers=headers
)
print(f"Logout Status: {response.status_code}")
```

---

## 10. ملاحظات هامة

1. **التوقيت:** جميع التواريخ والأوقات بتنسيق ISO 8601 مع المنطقة الزمنية (Z = UTC)
2. **التوكن:** صلاحية Access Token = ساعة واحدة، Refresh Token = 7 أيام
3. **الترقيم:** يبدأ الترقيم للصفحات من 1
4. **الاسم الرباعي:** يجب أن يحتوي على 4 أسماء على الأقل
5. **أنواع الحجز:** `full_day`, `half_day`, `hourly`
6. **أنواع العقارات:** `chalet`, `garden`, `istiraha`
