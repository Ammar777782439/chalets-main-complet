from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Div, Submit, HTML
from .models import Booking, Payment
from portfolio.models import Property
import math




class PaymentForm(forms.ModelForm):
    """نموذج تفاصيل الدفع عبر التحويل البنكي"""
    
    class Meta:
        model = Payment
        fields = ['transaction_id', 'payer_full_name', 'payer_phone_number']
        widgets = {
            'transaction_id': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
                    'placeholder': 'أدخل رقم عملية التحويل'
                }
            ),
            'payer_full_name': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
                    'placeholder': 'أدخل اسم المحول الرباعي'
                }
            ),
            'payer_phone_number': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
                    'placeholder': 'مثال: 777123456 أو 967777123456',
                    'inputmode': 'numeric',
                    'autocomplete': 'tel'
                }
            ),
        }
        labels = {
            'transaction_id': 'رقم عملية التحويل',
            'payer_full_name': 'اسم المحول (رباعي)',
            'payer_phone_number': 'رقم هاتف المحول',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # إضافة علامة النجمة للحقول المطلوبة
        for field_name, field in self.fields.items():
            if field.required:
                field.label += ' *'
        
        # إعداد crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'
        self.helper.layout = Layout(
            HTML('<div class="alert alert-info mb-4"><i class="fas fa-info-circle"></i> يرجى ملء جميع البيانات بدقة للتأكد من معالجة الدفع بنجاح</div>'),
            Fieldset(
                'تفاصيل التحويل البنكي',
                Row(
                    Column('transaction_id', css_class='form-group col-md-12 mb-4'),
                    css_class='form-row'
                ),
                Row(
                    Column('payer_full_name', css_class='form-group col-md-6 mb-4'),
                    Column('payer_phone_number', css_class='form-group col-md-6 mb-4'),
                    css_class='form-row'
                ),
                css_class='border rounded-lg p-4 mb-4 bg-gray-50'
            ),
            Div(
                Submit('submit', 'تأكيد بيانات الدفع', css_class='btn btn-success btn-lg w-full'),
                css_class='text-center mt-6'
            )
        )
    
    def clean_payer_full_name(self):
        """التحقق من أن اسم المحول يحتوي على أربعة أجزاء منفصلة"""
        payer_name = self.cleaned_data.get('payer_full_name')
        payer_name = (payer_name or '').strip()
        
        if payer_name:
            name_parts = payer_name.split()
            if len(name_parts) < 4:
                raise ValidationError('يرجى إدخال اسم المحول الرباعي كاملاً.')
            
            # التحقق من أن كل جزء من الاسم يحتوي على أحرف فقط
            for part in name_parts:
                if not part.replace(' ', '').isalpha():
                    raise ValidationError('يجب أن يحتوي الاسم على أحرف فقط.')
        
        return payer_name
    
    def clean_payer_phone_number(self):
        """التحقق من صحة رقم هاتف المحول"""
        phone = self.cleaned_data.get('payer_phone_number')
        phone = (phone or '').strip()
        
        if phone:
            # إزالة المسافات والرموز
            phone = phone.replace(' ', '').replace('-', '').replace('+', '')
            
            # التحقق من أن الرقم يبدأ بـ 77, 73, 70, 71, 78 أو 967
            valid_prefixes = ['77', '73', '70', '71', '78']
            is_valid = False
            
            # فحص الأرقام المحلية (9 أرقام)
            if len(phone) == 9 and any(phone.startswith(prefix) for prefix in valid_prefixes):
                is_valid = True
            # فحص الأرقام الدولية (12 رقم مع 967)
            elif phone.startswith('967') and len(phone) == 12:
                local_part = phone[3:]
                if any(local_part.startswith(prefix) for prefix in valid_prefixes):
                    is_valid = True
            
            if not is_valid:
                raise ValidationError('يرجى إدخال رقم هاتف يمني صحيح (مثال: 777123456)')
        
        return phone
    
    def clean_transaction_id(self):
        """التحقق من أن رقم العملية غير مستخدم من قبل"""
        transaction_id = self.cleaned_data.get('transaction_id')
        transaction_id = (transaction_id or '').strip()
        
        if transaction_id:
            # التحقق من عدم وجود رقم العملية في النظام
            existing_payment = Payment.objects.filter(
                transaction_id=transaction_id,
                status__in=['pending', 'approved']
            ).exists()
            
            if existing_payment:
                raise ValidationError('رقم العملية هذا مستخدم من قبل. يرجى التأكد من الرقم.')
        
        return transaction_id


class PropertyBookingForm(forms.ModelForm):
    """نموذج حجز العقارات (شاليه/استراحة/حديقة) مع اختيار نوع الحجز وتحديد الفترة الزمنية"""

    # أسماء الضيوف، كل اسم في سطر مستقل
    guest_names = forms.CharField(
        required=False,
        label='أسماء الضيوف (اسم في كل سطر)',
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'مثال:\nمحمد أحمد علي\nسارة خالد عمر\n...'
        })
    )

    class Meta:
        model = Booking
        fields = ['booking_type', 'start_datetime', 'end_datetime', 'customer_name', 'customer_phone']
        widgets = {
            'booking_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200',
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
                'placeholder': 'الاسم الرباعي كما في الهوية',
                'autocomplete': 'name'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200 placeholder-gray-400',
                'placeholder': 'مثال: 777123456 أو 967777123456',
                'inputmode': 'numeric',
                'autocomplete': 'tel'
            }),
        }
        labels = {
            'booking_type': 'نوع الحجز',
            'start_datetime': 'وقت البدء',
            'end_datetime': 'وقت الانتهاء',
            'customer_name': 'اسم العميل (رباعي)',
            'customer_phone': 'رقم هاتف العميل',
        }

    def __init__(self, *args, **kwargs):
        self.property = kwargs.pop('property', None)
        super().__init__(*args, **kwargs)

        # إضافة علامة النجمة للحقول المطلوبة
        for field_name, field in self.fields.items():
            if field.required and field.label and not str(field.label).endswith('*'):
                field.label = f"{field.label} *"

        # crispy layout
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'
        self.helper.layout = Layout(
            Fieldset(
                'معلومات الحجز',
                Row(
                    Column('booking_type', css_class='form-group col-md-12 mb-4'),
                    css_class='form-row'
                ),
                Row(
                    Column('start_datetime', css_class='form-group col-md-6 mb-4'),
                    Column('end_datetime', css_class='form-group col-md-6 mb-4'),
                    css_class='form-row'
                ),
                Row(
                    Column('customer_name', css_class='form-group col-md-6 mb-4'),
                    Column('customer_phone', css_class='form-group col-md-6 mb-4'),
                    css_class='form-row'
                ),
                Row(
                    Column('guest_names', css_class='form-group col-md-12 mb-2'),
                    css_class='form-row'
                ),
                css_class='border rounded-lg p-4 mb-4 bg-gray-50'
            ),
            Div(
                Submit('submit', 'تأكيد الحجز', css_class='btn btn-primary btn-lg w-full'),
                css_class='text-center mt-6'
            )
        )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_datetime')
        end = cleaned.get('end_datetime')

        # parse from input type datetime-local may be naive; make aware
        if start and timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.get_current_timezone())
            cleaned['start_datetime'] = start
        if end and timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.get_current_timezone())
            cleaned['end_datetime'] = end

        if start and end:
            if end <= start:
                raise ValidationError('وقت الانتهاء يجب أن يكون بعد وقت البدء')
            if start < timezone.now():
                raise ValidationError('لا يمكن الحجز في وقت مضى')

            # Check overlap
            from .services import is_timeslot_available
            available = is_timeslot_available(
                property_obj=self.property,
                start_dt=start,
                end_dt=end,
                exclude_booking_id=self.instance.pk
            )
            if not available:
                raise ValidationError('عذراً، هذا العقار محجوز بالفعل في الفترة الزمنية المحددة. يرجى اختيار وقت آخر.')

        return cleaned

    def compute_total_price(self):
        """احسب السعر الإجمالي بناءً على نوع الحجز"""
        if not self.property:
            return None
        booking_type = self.cleaned_data.get('booking_type')
        start = self.cleaned_data.get('start_datetime')
        end = self.cleaned_data.get('end_datetime')
        if not booking_type:
            return None
        if booking_type == 'hourly' and start and end and self.property.price_per_hour:
            hours = (end - start).total_seconds() / 3600.0
            return math.ceil(hours) * self.property.price_per_hour
        if booking_type == 'half_day' and self.property.price_half_day:
            return self.property.price_half_day
        # full_day and overnight fallback to per_day
        return self.property.price_per_day or 0