from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import PaymentProvider, Booking, Payment


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    """إدارة وسطاء الدفع"""
    list_display = ('name', 'provider_type', 'icon_preview', 'account_number', 'is_active', 'created_at')
    list_filter = ('provider_type', 'is_active', 'created_at')
    search_fields = ('name', 'account_number')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('معلومات الوسيط', {
            'fields': ('name', 'provider_type', 'icon', 'icon_preview', 'account_number')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('icon_preview',)
    
    def icon_preview(self, obj):
        """عرض معاينة أيقونة وسيط الدفع"""
        if obj.icon:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 4px; object-fit: cover;" />',
                obj.icon.url
            )
        return "لا توجد أيقونة"
    icon_preview.short_description = 'معاينة الأيقونة'


class PaymentInline(admin.StackedInline):
    """إدارة الدفع داخل صفحة الحجز"""
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('معلومات الدفع', {
            'fields': ('payment_method', 'provider', 'status', 'is_valid')
        }),
        ('تفاصيل التحويل البنكي', {
            'fields': ('transaction_id', 'payer_full_name', 'payer_phone_number'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """إدارة الحجوزات"""
    list_display = ('booking_id', 'user', 'property', 'booking_date', 'customer_name', 'customer_phone', 'total_price', 'status_badge', 'created_at')
    list_filter = ('status', 'booking_date', 'created_at', 'property', 'user')
    search_fields = ('customer_name', 'customer_phone', 'property__name', 'user__username', 'user__email')
    ordering = ('-created_at',)
    date_hierarchy = 'booking_date'
    
    fieldsets = (
        ('معلومات الحجز', {
            'fields': ('property', 'booking_date', 'start_datetime', 'end_datetime', 'booking_type', 'total_price', 'status')
        }),
        ('معلومات العميل', {
            'fields': ('user', 'customer_name', 'customer_phone')
        }),
        ('التواريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    inlines = [PaymentInline]
    
    def booking_id(self, obj):
        """عرض رقم الحجز بتنسيق مميز"""
        return f"#{obj.id:05d}"
    booking_id.short_description = 'رقم الحجز'
    
    def status_badge(self, obj):
        """عرض حالة الحجز بألوان مميزة"""
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'الحالة'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """إدارة المدفوعات"""
    list_display = ('booking_id', 'payment_method', 'provider', 'status_badge', 'is_valid_badge', 'created_at')
    list_filter = ('payment_method', 'status', 'is_valid', 'created_at', 'provider')
    search_fields = ('booking__customer_name', 'booking__customer_phone', 'transaction_id', 'payer_full_name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات الحجز', {
            'fields': ('booking',)
        }),
        ('معلومات الدفع', {
            'fields': ('payment_method', 'provider', 'status', 'is_valid')
        }),
        ('تفاصيل التحويل البنكي', {
            'fields': ('transaction_id', 'payer_full_name', 'payer_phone_number'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    actions = ['approve_payment', 'reject_payment']
    
    def booking_id(self, obj):
        """عرض رقم الحجز المرتبط"""
        return f"#{obj.booking.id:05d}"
    booking_id.short_description = 'رقم الحجز'
    
    def status_badge(self, obj):
        """عرض حالة الدفع بألوان مميزة"""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'حالة الدفع'
    
    def is_valid_badge(self, obj):
        """عرض حالة التحقق بألوان مميزة"""
        if obj.is_valid:
            return format_html('<span style="color: green; font-weight: bold;">✓ تم التحقق</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ لم يتم التحقق</span>')
    is_valid_badge.short_description = 'التحقق'
    
    def approve_payment(self, request, queryset):
        """إجراء إدارة لاعتماد الدفع"""
        updated_payments = 0
        updated_bookings = 0
        
        for payment in queryset:
            if payment.status != 'approved':
                # تحديث حالة الدفع
                payment.status = 'approved'
                payment.is_valid = True
                payment.save()
                updated_payments += 1
                
                # تحديث حالة الحجز المرتبط
                booking = payment.booking
                # تحديث حالة الدفع في الحجز حسب السيناريو
                if booking.payment_method == 'cash':
                    booking.payment_status = 'deposit_paid'
                else:
                    booking.payment_status = 'paid'
                if booking.status != 'confirmed':
                    booking.status = 'confirmed'
                booking.save()
                updated_bookings += 1
        
        if updated_payments > 0:
            messages.success(
                request,
                f'تم اعتماد {updated_payments} دفعة وتأكيد {updated_bookings} حجز بنجاح.'
            )
        else:
            messages.info(request, 'لا توجد دفعات جديدة لاعتمادها.')
    
    approve_payment.short_description = 'اعتماد الدفع المحدد'
    
    def reject_payment(self, request, queryset):
        """إجراء إدارة لرفض الدفع"""
        updated_payments = 0
        updated_bookings = 0
        
        for payment in queryset:
            if payment.status != 'rejected':
                # تحديث حالة الدفع
                payment.status = 'rejected'
                payment.is_valid = False
                payment.save()
                updated_payments += 1
                
                # تحديث حالة الحجز المرتبط
                booking = payment.booking
                booking.payment_status = 'pending'
                if booking.status != 'cancelled':
                    booking.status = 'cancelled'
                booking.save()
                updated_bookings += 1
        
        if updated_payments > 0:
            messages.warning(
                request,
                f'تم رفض {updated_payments} دفعة وإلغاء {updated_bookings} حجز.'
            )
        else:
            messages.info(request, 'لا توجد دفعات جديدة لرفضها.')
    
    reject_payment.short_description = 'رفض الدفع المحدد'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'provider')
