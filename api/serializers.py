import math
import secrets
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from accounts.models import UserProfile
from portfolio.models import Property, Amenity, GalleryImage, PropertyReview
from booking.models import Booking, BookingGuest, Payment, PaymentProvider
from booking.services import is_timeslot_available
from django.utils import timezone

# Auth Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'full_name', 'phone_number']

    def validate_full_name(self, value):
        names = value.strip().split()
        if len(names) < 4:
            raise serializers.ValidationError('يجب إدخال الاسم الرباعي (أربعة أسماء على الأقل)')
        return value

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        phone_number = validated_data.pop('phone_number', '')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(password=password, **validated_data)
        
        if not hasattr(user, 'userprofile'):
            UserProfile.objects.create(user=user, full_name=full_name, phone_number=phone_number)
        else:
            user.userprofile.full_name = full_name
            user.userprofile.phone_number = phone_number
            user.userprofile.save()
            
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("بيانات الدخول غير صحيحة")

# User Serializers
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone_number', 'address', 'date_of_birth', 'profile_picture', 'username', 'email']
        read_only_fields = ['username', 'email']

# Property Serializers
class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

class GalleryImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'image_url', 'caption']
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
             return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class PropertyListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    amenities = AmenitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = ['id', 'name', 'description', 'city', 'price_per_day', 'main_image', 'property_type', 'capacity', 'amenities', 'is_verified_by_platform', 'privacy_rating']
        
    def get_main_image(self, obj):
        request = self.context.get('request')
        if obj.main_image:
             return request.build_absolute_uri(obj.main_image.url) if request else obj.main_image.url
        return None

class PropertyDetailSerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True, read_only=True)
    gallery_images = GalleryImageSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    reviews_avg = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = '__all__'
    
    def get_main_image(self, obj):
        request = self.context.get('request')
        if obj.main_image:
             return request.build_absolute_uri(obj.main_image.url) if request else obj.main_image.url
        return None
        
    def get_reviews_avg(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)

# Review Serializers
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.userprofile.full_name', read_only=True)
    
    class Meta:
        model = PropertyReview
        fields = ['id', 'property', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'is_approved', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Unique constraint check is in model, but we can catch IntegrityError or let DRF validator handle it if configured
        return super().create(validated_data)

# Booking Serializers
class BookingGuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingGuest
        fields = ['id', 'serial', 'name', 'code']
        read_only_fields = ['serial', 'code']

class BookingSerializer(serializers.ModelSerializer):
    guests = BookingGuestSerializer(many=True, read_only=True)
    guest_names = serializers.CharField(write_only=True, required=False, allow_blank=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'property', 'property_name', 'start_datetime', 'end_datetime', 
            'booking_type', 'customer_name', 'customer_phone', 
            'total_price', 'status', 'payment_status', 'deposit_amount', 
            'guests', 'guest_names', 'created_at'
        ]
        read_only_fields = ['user', 'status', 'total_price', 'payment_status', 'deposit_amount', 'created_at']

    def validate(self, data):
        start = data.get('start_datetime')
        end = data.get('end_datetime')
        property_obj = data.get('property')
        
        if self.instance and not property_obj:
            property_obj = self.instance.property

        if start and end:
            if end <= start:
                raise serializers.ValidationError({'end_datetime': 'وقت الانتهاء يجب أن يكون بعد وقت البدء'})
            if start < timezone.now():
                raise serializers.ValidationError({'start_datetime': 'لا يمكن الحجز في وقت مضى'})
            
            if property_obj:
                 available = is_timeslot_available(
                    property_obj=property_obj,
                    start_dt=start,
                    end_dt=end,
                    exclude_booking_id=self.instance.pk if self.instance else None
                )
                 if not available:
                    raise serializers.ValidationError('عذراً، هذا العقار محجوز بالفعل في الفترة الزمنية المحددة. يرجى اختيار وقت آخر.')

        return data

    def create(self, validated_data):
        guest_names = validated_data.pop('guest_names', '')
        validated_data['user'] = self.context['request'].user
        
        property_obj = validated_data.get('property')
        booking_type = validated_data.get('booking_type')
        start = validated_data.get('start_datetime')
        end = validated_data.get('end_datetime')
        
        # Legacy backfill
        if start:
            validated_data['booking_date'] = start.date()

        total_price = 0
        if property_obj and booking_type:
            if booking_type == 'hourly' and start and end and property_obj.price_per_hour:
                hours = (end - start).total_seconds() / 3600.0
                total_price = math.ceil(hours) * float(property_obj.price_per_hour)
            elif booking_type == 'half_day' and property_obj.price_half_day:
                total_price = property_obj.price_half_day
            else:
                 total_price = property_obj.price_per_day or 0
        
        validated_data['total_price'] = total_price
        
        booking = super().create(validated_data)
        
        if guest_names:
            lines = [ln.strip() for ln in guest_names.splitlines() if ln and ln.strip()]
            if lines:
                existing_codes = set()
                serial = 1
                for name in lines:
                    code = gen_code()
                    while code in existing_codes or BookingGuest.objects.filter(booking=booking, code=code).exists():
                         code = gen_code()
                    existing_codes.add(code)
                    BookingGuest.objects.create(
                        booking=booking,
                        serial=serial,
                        name=name,
                        code=code,
                    )
                    serial += 1
                    
        return booking

def gen_code():
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(alphabet) for _ in range(6))

class BookingDetailSerializer(serializers.ModelSerializer):
    guests = BookingGuestSerializer(many=True, read_only=True)
    property = PropertyDetailSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'

# Payment Serializers
class PaymentProviderSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = PaymentProvider
        fields = ['id', 'name', 'account_number', 'provider_type', 'icon', 'icon_url']
        
    def get_icon_url(self, obj):
        request = self.context.get('request')
        if obj.icon:
             return request.build_absolute_uri(obj.icon.url) if request else obj.icon.url
        return None

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['booking', 'status', 'is_valid']
