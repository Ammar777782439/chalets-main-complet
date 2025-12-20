from django import forms
from decimal import Decimal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Div, Submit, HTML
from .models import Property, Amenity, PropertyReview
from django.db.models import Q
from .widgets import LocationPickerField




class ContactForm(forms.Form):
    """نموذج التواصل"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'الاسم الكامل'
        }),
        label='الاسم *'
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'رقم الهاتف'
        }),
        label='رقم الهاتف *'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'اكتب رسالتك هنا...',
            'rows': 5
        }),
        label='الرسالة *'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # إعداد crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'
        self.helper.layout = Layout(
            HTML('<div class="text-center mb-6"><h3 class="text-2xl font-bold text-gray-800 mb-2">تواصل معنا</h3><p class="text-gray-600">نحن هنا لمساعدتك في أي استفسار</p></div>'),
            Fieldset(
                'معلومات التواصل',
                Row(
                    Column('name', css_class='form-group col-md-6 mb-4'),
                    Column('phone', css_class='form-group col-md-6 mb-4'),
                    css_class='form-row'
                ),
                Row(
                    Column('message', css_class='form-group col-md-12 mb-4'),
                    css_class='form-row'
                ),
                css_class='border rounded-lg p-4 mb-4 bg-gray-50'
            ),
            Div(
                Submit('submit', 'إرسال الرسالة', css_class='btn btn-primary btn-lg w-full'),
                css_class='text-center mt-6'
            )
        )



class PropertyReviewForm(forms.ModelForm):
    class Meta:
        model = PropertyReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl', 'placeholder': 'اكتب رأيك هنا...'}),
        }


class PropertySearchForm(forms.Form):
    """Filters for Property listing (chalets/gardens/istirahat)."""
    search = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={
        'placeholder': 'ابحث عن شاليه/حديقة/استراحة...',
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl'
    }), label='البحث')

    booking_type = forms.ChoiceField(required=False, choices=[
        ('', 'كل الأنواع'),
        ('hourly', 'بالساعة'),
        ('half_day', 'نصف يوم'),
        ('full_day', 'يوم كامل'),
        ('overnight', 'مبيت'),
    ], widget=forms.Select(attrs={'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl'}), label='نوع الحجز')

    start_datetime = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={
        'type': 'datetime-local',
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl'
    }), label='وقت البدء')
    end_datetime = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={
        'type': 'datetime-local',
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl'
    }), label='وقت الانتهاء')

    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(), required=False,
        widget=forms.SelectMultiple(attrs={'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl'}),
        label='المزايا'
    )

    city = forms.ChoiceField(required=False, choices=[
        ('', 'كل المدن'), ('Sana\'a', 'صنعاء'), ('Ibb', 'إب'), ('Aden', 'عدن'), ('Taiz', 'تعز'), ('Hodeidah', 'الحديدة')
    ], widget=forms.Select(attrs={'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl'}), label='المدينة')

    radius_km = forms.IntegerField(required=False, min_value=1, max_value=100, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl', 'placeholder': '10'
    }), label='نطاق البحث (كم)')

    min_privacy = forms.IntegerField(required=False, min_value=1, max_value=5, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl', 'placeholder': '1-5'
    }), label='أدنى خصوصية')

    is_verified_by_platform = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={}), label='عرض المعتمد فقط')

    min_price = forms.DecimalField(required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl', 'placeholder': 'حد أدنى'
    }), label='السعر الأدنى')
    max_price = forms.DecimalField(required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl', 'placeholder': 'حد أقصى'
    }), label='السعر الأعلى')

    min_capacity = forms.IntegerField(required=False, min_value=1, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl', 'placeholder': 'الحد الأدنى للسعة'
    }), label='السعة الدنيا')
    max_capacity = forms.IntegerField(required=False, min_value=1, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl', 'placeholder': 'الحد الأعلى للسعة'
    }), label='السعة العليا')

    ordering = forms.ChoiceField(required=False, choices=[
        ('name', 'الاسم (أ-ي)'), ('-name', 'الاسم (ي-أ)'),
        ('price', 'السعر (الأقل أولاً)'), ('-price', 'السعر (الأعلى أولاً)'),
        ('rating', 'التقييم (الأعلى أولاً)'), ('-rating', 'التقييم (الأدنى أولاً)'),
        ('-created_at', 'الأحدث أولاً')
    ], widget=forms.Select(attrs={'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl'}), label='ترتيب حسب')

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_datetime')
        end = cleaned.get('end_datetime')
        if start and end and end <= start:
            raise forms.ValidationError('وقت الانتهاء يجب أن يكون بعد وقت البدء')
        min_price = cleaned.get('min_price')
        max_price = cleaned.get('max_price')
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError('الحد الأدنى للسعر يجب أن يكون أقل من الحد الأعلى')
        min_capacity = cleaned.get('min_capacity')
        max_capacity = cleaned.get('max_capacity')
        if min_capacity and max_capacity and min_capacity > max_capacity:
            raise forms.ValidationError('الحد الأدنى للسعة يجب أن يكون أقل من الحد الأعلى')
        return cleaned


class PropertyAdminForm(forms.ModelForm):
    """
    Custom admin form for Property model with map-based location picker.
    """
    
    location = LocationPickerField(
        label="الموقع",
        help_text="اختر موقع العقار من الخريطة أو أدخل العنوان",
        required=False
    )
    
    class Meta:
        model = Property
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['location'].initial = [
                self.instance.latitude,
                self.instance.longitude,
                self.instance.address
            ]
        
        if 'latitude' in self.fields:
            self.fields['latitude'].widget = forms.HiddenInput()
        if 'longitude' in self.fields:
            self.fields['longitude'].widget = forms.HiddenInput()
        if 'address' in self.fields:
            self.fields['address'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        location_data = cleaned_data.get('location')
        
        if location_data and isinstance(location_data, (list, tuple)) and len(location_data) >= 3:
            latitude, longitude, address = location_data[0], location_data[1], location_data[2]
            cleaned_data['latitude'] = latitude
            cleaned_data['longitude'] = longitude
            cleaned_data['address'] = address or ''
        else:
            cleaned_data['latitude'] = None
            cleaned_data['longitude'] = None
            cleaned_data['address'] = ''
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        location_data = self.cleaned_data.get('location')
        if location_data and isinstance(location_data, (list, tuple)) and len(location_data) >= 3:
            latitude, longitude, address = location_data[0], location_data[1], location_data[2]
            instance.latitude = latitude
            instance.longitude = longitude
            instance.address = address or ''
        else:
            if not hasattr(instance, 'latitude') or instance.latitude is None:
                instance.latitude = None
            if not hasattr(instance, 'longitude') or instance.longitude is None:
                instance.longitude = None
            if not hasattr(instance, 'address') or not instance.address:
                instance.address = ''
        
        if commit:
            instance.save()
         
        return instance


class OwnerPropertyForm(forms.ModelForm):
    # حقل اختيار الموقع عبر الخريطة (ليس حقلاً في قاعدة البيانات)
    location = LocationPickerField(
        label="الموقع",
        help_text="اختر الموقع من الخريطة أو أدخل العنوان",
        required=False
    )

    class Meta:
        model = Property
        fields = [
            'name', 'description', 'property_type', 'capacity',
            'main_image', 'amenities', 'city',
            'price_per_hour', 'price_half_day', 'price_per_day', 'is_price_negotiable',
            'privacy_rating', 'checkin_time', 'checkout_time',
        ]
        labels = {
            'name': 'اسم العقار',
            'description': 'وصف العقار',
            'property_type': 'نوع العقار',
            'capacity': 'السعة (عدد الأشخاص)',
            'main_image': 'الصورة الرئيسية',
            'amenities': 'المزايا',
            'city': 'المدينة',
            'price_per_hour': 'سعر الساعة',
            'price_half_day': 'سعر نصف اليوم',
            'price_per_day': 'سعر اليوم/المبيت',
            'is_price_negotiable': 'السعر قابل للتفاوض؟',
            'privacy_rating': 'مستوى الخصوصية (1-5)',
            'checkin_time': 'وقت الدخول',
            'checkout_time': 'وقت الخروج',
        }
        help_texts = {
            'description': 'اكتب وصفًا واضحًا ومختصرًا يبرز مميزات العقار.',
            'amenities': 'اختر جميع المزايا المتوفرة في العقار.',
            'price_per_hour': 'اتركها فارغة إذا لم تدعم الحجز بالساعة.',
            'price_half_day': 'اتركها فارغة إذا لم تدعم الحجز نصف يوم.',
            'price_per_day': 'المبلغ لليوم الكامل أو المبيت.',
            'privacy_rating': 'اختر مستوى الخصوصية من 1 (منخفض) إلى 5 (مرتفع).',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'اسم واضح وجذاب (مثال: شاليه الياسمين)'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'صف العقار والمزايا القريبة ومناسباته'
            }),
            'property_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'capacity': forms.NumberInput(attrs={
                'min': 1,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'عدد الأشخاص'
            }),
            'main_image': forms.ClearableFileInput(attrs={
                'class': 'w-full',
                'accept': 'image/*'
            }),
            'amenities': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'اسم المدينة'
            }),
            'price_per_hour': forms.NumberInput(attrs={
                'step': '0.01',
                'min': 0,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'مثال: 150.00'
            }),
            'price_half_day': forms.NumberInput(attrs={
                'step': '0.01',
                'min': 0,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'مثال: 300.00'
            }),
            'price_per_day': forms.NumberInput(attrs={
                'step': '0.01',
                'min': 0,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'مثال: 600.00'
            }),
            'is_price_negotiable': forms.CheckboxInput(attrs={}),
            'privacy_rating': forms.NumberInput(attrs={
                'type': 'number',
                'min': 1,
                'max': 5,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '1-5'
            }),
            'checkin_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'checkout_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        owner_only = kwargs.pop('owner_only', False)
        super().__init__(*args, **kwargs)
        # تهيئة قيمة الموقع من الكائن الحالي
        if self.instance and getattr(self.instance, 'pk', None):
            self.fields['location'].initial = [
                getattr(self.instance, 'latitude', None),
                getattr(self.instance, 'longitude', None),
                getattr(self.instance, 'address', ''),
            ]
        # اجعل قائمة المزايا خاصة بالمالك (وتتضمن العامة)
        if 'amenities' in self.fields:
            qs = Amenity.objects.all()
            if user is not None:
                if owner_only:
                    qs = qs.filter(owner=user)
                else:
                    qs = qs.filter(Q(owner=user) | Q(owner__isnull=True))
            self.fields['amenities'].queryset = qs.order_by('name')
        for name, field in self.fields.items():
            if field.required and field.label and not str(field.label).endswith('*'):
                field.label = f"{field.label} *"

    def save(self, commit=True):
        instance = super().save(commit=False)
        loc = self.cleaned_data.get('location')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 3:
            lat, lng, addr = loc[0], loc[1], loc[2]
            instance.latitude = lat if lat is not None else None
            instance.longitude = lng if lng is not None else None
            instance.address = addr or ''
        else:
            # إذا لم يتم تحديد موقع، اترك القيم كما هي (أو امسحها إن أردت)
            pass
        if commit:
            instance.save()
            self.save_m2m()
        return instance
