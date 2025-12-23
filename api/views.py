from rest_framework import viewsets, generics, status, permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from accounts.models import UserProfile
from portfolio.models import Property, Amenity, PropertyReview
from booking.models import Booking, Payment, PaymentProvider, BookingGuest
from booking.services import is_timeslot_available
from booking.utils import generate_qr_code_for_guest

from .serializers import *
from .permissions import *
from .pagination import StandardResultsSetPagination
from .filters import PropertyFilter

# Auth
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

class LoginView(TokenObtainPairView):
    pass

class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# User
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        
        if not old_password or not new_password:
             return Response({"error": "يجب إدخال كلمة المرور القديمة والجديدة"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({"old_password": ["كلمة المرور القديمة غير صحيحة"]}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        user.save()
        return Response({"status": "تم تغيير كلمة المرور بنجاح"}, status=status.HTTP_200_OK)

class DeleteAccountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Properties
class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Property.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['name', 'description', 'city']
    ordering_fields = ['price_per_day', 'created_at']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        return PropertyListSerializer

    @action(detail=True, methods=['get'])
    def gallery(self, request, pk=None):
        property_obj = self.get_object()
        images = property_obj.gallery_images.all()
        serializer = GalleryImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)

class AmenityListView(generics.ListAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    pagination_class = None 

# Reviews
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['property']

    def get_queryset(self):
        return PropertyReview.objects.filter(is_approved=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Bookings
class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingOwner]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
             return Booking.objects.none()
        return Booking.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookingDetailSerializer
        return BookingSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'cancelled':
            return Response({"error": "الحجز ملغي بالفعل"}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'cancelled'
        booking.save()
        return Response({"status": "تم إلغاء الحجز"})

    @action(detail=False, methods=['post'], url_path='check-availability')
    def check_availability(self, request):
        property_id = request.data.get('property_id')
        start_str = request.data.get('start_datetime')
        end_str = request.data.get('end_datetime')
        
        if not all([property_id, start_str, end_str]):
             return Response({"error": "يجب إرسال property_id, start_datetime, end_datetime"}, status=status.HTTP_400_BAD_REQUEST)
             
        try:
            start_dt = parse_datetime(start_str)
            end_dt = parse_datetime(end_str)
            
            if timezone.is_naive(start_dt):
                start_dt = timezone.make_aware(start_dt)
            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt)
                
            property_obj = get_object_or_404(Property, pk=property_id)
            
            is_available = is_timeslot_available(
                property_obj=property_obj,
                start_dt=start_dt,
                end_dt=end_dt
            )
            return Response({"available": is_available})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BookingCancelView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({"error": "booking_id required"}, status=400)
        
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        if booking.status == 'cancelled':
            return Response({"error": "الحجز ملغي بالفعل"}, status=400)
            
        booking.status = 'cancelled'
        booking.save()
        return Response({"status": "تم إلغاء الحجز"})

# Payments
class PaymentProviderListView(generics.ListAPIView):
    queryset = PaymentProvider.objects.filter(is_active=True)
    serializer_class = PaymentProviderSerializer
    pagination_class = None

class PaymentSubmitView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        booking_id = self.request.data.get('booking')
        booking = get_object_or_404(Booking, id=booking_id, user=self.request.user)
        
        if hasattr(booking, 'payment'):
             # If payment exists, maybe update it? Or fail?
             # For simplicity, create/update. OneToOne.
             # If create, it will fail IntegrityError if exists.
             # But serializer handles validation of OneToOne?
             # Actually OneToOne unique constraint.
             pass

        serializer.save(booking=booking, status='pending')
        
        booking.payment_status = 'pending'
        booking.save()

class PaymentStatusView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        booking_id = request.query_params.get('booking_id')
        if not booking_id:
             return Response({"error": "booking_id required"}, status=400)
        
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        try:
            payment = booking.payment
            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response({"error": "No payment found"}, status=404)

# QR Code
class GuestQRCodeView(views.APIView):
    """Generate QR code for a guest"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, code):
        try:
            guest = BookingGuest.objects.select_related('booking', 'booking__property').get(code=code)
            
            # Verify user has permission (booking owner or property owner)
            if guest.booking.user != request.user and guest.booking.property.owner != request.user:
                return Response({"error": "غير مصرح بالوصول"}, status=403)
            
            qr_code = generate_qr_code_for_guest(guest, request)
            
            return Response({
                'qr_code': qr_code,
                'guest_name': guest.name,
                'code': guest.code,
                'booking_id': guest.booking.id,
                'property_name': guest.booking.property.name if guest.booking.property else None
            })
            
        except BookingGuest.DoesNotExist:
            return Response({"error": "الرمز غير موجود"}, status=404)
