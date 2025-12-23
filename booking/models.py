from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from portfolio.models import Property


class PaymentProvider(models.Model):
    """نموذج يمثل مقدمي خدمات الدفع"""
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payment_providers',
        null=True,
        blank=True,
        verbose_name="المالك"
    )
    name = models.CharField(max_length=100, verbose_name="اسم الوسيط")
    icon = models.ImageField(upload_to='payment_providers/', blank=True, null=True, verbose_name="أيقونة الوسيط")
    account_number = models.CharField(max_length=50, verbose_name="رقم الحساب")
    PROVIDER_TYPE_CHOICES = [
        ('bank', 'بنك'),
        ('wallet', 'محفظة إلكترونية'),
    ]
    provider_type = models.CharField(max_length=10, choices=PROVIDER_TYPE_CHOICES, default='bank', verbose_name="نوع الوسيط")
    is_active = models.BooleanField(default=True, verbose_name="نشط؟")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "وسيط الدفع"
        verbose_name_plural = "وسطاء الدفع"
        ordering = ['name']

    def __str__(self):
        return self.name


class Booking(models.Model):
    """نموذج يمثل حجوزات العقارات"""
    STATUS_CHOICES = [
        ('pending', 'في انتظار التأكيد'),
        ('confirmed', 'مؤكد'),
        ('cancelled', 'ملغي'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="المستخدم",
        null=True,
        blank=True
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="العقار المحجوز"
    )
    booking_date = models.DateField(verbose_name="تاريخ الحجز")
    start_datetime = models.DateTimeField(null=True, blank=True, verbose_name="وقت البدء")
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name="وقت الانتهاء")
    BOOKING_TYPE_CHOICES = [
        ('hourly', 'بالساعة'),
        ('half_day', 'نصف يوم'),
        ('full_day', 'يوم كامل'),
        ('overnight', 'مبيت'),
    ]
    booking_type = models.CharField(
        max_length=20,
        choices=BOOKING_TYPE_CHOICES,
        default='full_day',
        verbose_name="نوع الحجز"
    )
    customer_name = models.CharField(max_length=200, verbose_name="اسم العميل (رباعي)")
    customer_phone = models.CharField(max_length=20, verbose_name="رقم هاتف العميل")
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="المبلغ الإجمالي"
    )
    PAYMENT_METHOD_CHOICES = [
        ('wallet_transfer', 'تحويل محفظة'),
        ('bank_transfer', 'تحويل بنكي'),
        ('cash', 'نقداً'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'قيد المعالجة'),
        ('deposit_paid', 'تم دفع العربون'),
        ('paid', 'مدفوع بالكامل'),
        ('cash_on_arrival', 'دفع عند الوصول'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer', verbose_name="طريقة الدفع")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="حالة الدفع")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="مبلغ العربون")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        verbose_name="حالة الحجز"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "حجز"
        verbose_name_plural = "الحجوزات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', 'start_datetime']),
            models.Index(fields=['property', 'end_datetime']),
        ]

    def __str__(self):
        if self.start_datetime and self.end_datetime and self.property:
            return f"{self.customer_name} - {self.property.name} - {self.start_datetime:%Y-%m-%d %H:%M} → {self.end_datetime:%H:%M}"
        return f"{self.customer_name} - {self.booking_date}"

    def clean(self):
        """Validate booking timing and availability"""
        # Legacy date-only validation
        if self.booking_date and self.booking_date < timezone.now().date():
            raise ValidationError({'booking_date': 'لا يمكن حجز تاريخ في الماضي'})

        # Timeslot validation when provided
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError({'end_datetime': 'وقت الانتهاء يجب أن يكون بعد وقت البدء'})

            # Prevent past timeslot bookings
            if self.start_datetime < timezone.now():
                raise ValidationError({'start_datetime': 'لا يمكن الحجز في وقت مضى'})

            # Check overlaps via service
            try:
                from .services import is_timeslot_available
            except Exception:
                is_timeslot_available = None

            if is_timeslot_available is not None:
                available = is_timeslot_available(
                    property_obj=self.property if self.property_id else None,
                    start_dt=self.start_datetime,
                    end_dt=self.end_datetime,
                    exclude_booking_id=self.pk,
                )
                if not available:
                    raise ValidationError({'start_datetime': 'الوقت المحدد غير متاح', 'end_datetime': 'الوقت المحدد غير متاح'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BookingGuest(models.Model):
    """ضيف مرتبط بحجز، مع رقم تسلسلي ورمز دعوة للطباعة/التحقق"""
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='guests',
        verbose_name="الحجز"
    )
    serial = models.PositiveIntegerField(verbose_name="الرقم التسلسلي")
    name = models.CharField(max_length=200, verbose_name="اسم الضيف")
    code = models.CharField(max_length=20, verbose_name="رمز الدعوة")
    checkin_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت الدخول")
    checkout_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت الخروج")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ضيف الحجز"
        verbose_name_plural = "ضيوف الحجز"
        ordering = ['serial']
        constraints = [
            models.UniqueConstraint(fields=['booking', 'serial'], name='unique_guest_serial_per_booking'),
            models.UniqueConstraint(fields=['booking', 'code'], name='unique_guest_code_per_booking'),
        ]
        indexes = [
            models.Index(fields=['booking', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Payment(models.Model):
    """نموذج يمثل معاملات الدفع"""
    PAYMENT_METHOD_CHOICES = [
        ('wallet_transfer', 'تحويل محفظة'),
        ('bank_transfer', 'تحويل بنكي'),
        ('cash', 'نقداً'),
    ]

    STATUS_CHOICES = [
        ('pending', 'في انتظار المراجعة'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
    ]

    booking = models.OneToOneField(
        Booking, 
        on_delete=models.CASCADE, 
        verbose_name="الحجز"
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        verbose_name="طريقة الدفع"
    )
    provider = models.ForeignKey(
        PaymentProvider, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="وسيط الدفع"
    )
    transaction_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="رقم عملية التحويل"
    )
    payer_full_name = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="اسم المحول (رباعي)"
    )
    payer_phone_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name="رقم هاتف المحول"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المبلغ")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        verbose_name="حالة الدفع"
    )
    is_valid = models.BooleanField(default=False, verbose_name="تم التحقق؟")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "الدفعات"
        ordering = ['-created_at']

    def __str__(self):
        return f"دفعة {self.booking.customer_name} - {self.get_payment_method_display()}"

    def clean(self):
        """التحقق من صحة بيانات الدفع بناءً على طريقة الدفع"""
        if self.payment_method == 'bank_transfer':
            if not self.transaction_id:
                raise ValidationError({'transaction_id': 'رقم عملية التحويل مطلوب للتحويل البنكي'})
            if not self.payer_full_name:
                raise ValidationError({'payer_full_name': 'اسم المحول مطلوب للتحويل البنكي'})
            if not self.provider:
                raise ValidationError({'provider': 'وسيط الدفع مطلوب للتحويل البنكي'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
