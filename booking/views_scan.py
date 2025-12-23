from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import BookingGuest, Booking
from portfolio.models import Property
import json


class QRScannerView(LoginRequiredMixin, TemplateView):
    """واجهة مسح QR codes لأصحاب الشاليهات"""
    template_name = 'booking/qr_scanner.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get properties owned by the user
        user_properties = self.request.user.owned_properties.all()
        context['properties'] = user_properties
        return context


def verify_guest_code(request):
    """التحقق من رمز الضيف ومسح الدخول/الخروج"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'غير مصرح'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'طريقة غير صحيحة'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        action = data.get('action')  # 'checkin' or 'checkout'
        
        if not code or action not in ['checkin', 'checkout']:
            return JsonResponse({'error': 'بيانات غير صحيحة'}, status=400)
        
        # Find guest by code
        guest = BookingGuest.objects.select_related(
            'booking', 
            'booking__property', 
            'booking__user'
        ).get(code=code)
        
        # Verify user owns the property
        if guest.booking.property.owner != request.user:
            return JsonResponse({'error': 'غير مصرح بالوصول لهذا الحجز'}, status=403)
        
        # Check booking status
        if guest.booking.status != 'confirmed':
            return JsonResponse({'error': 'الحجز غير مؤكد'}, status=400)
        
        # Perform action
        if action == 'checkin':
            if hasattr(guest, 'checkin_time') and guest.checkin_time:
                return JsonResponse({'error': 'الضيف قد سجل دخوله بالفعل'}, status=400)
            
            guest.checkin_time = timezone.now()
            guest.save(update_fields=['checkin_time'])
            
            return JsonResponse({
                'success': True,
                'message': 'تم تسجيل الدخول بنجاح',
                'guest': {
                    'name': guest.name,
                    'code': guest.code,
                    'booking_id': guest.booking.id,
                    'property_name': guest.booking.property.name,
                    'checkin_time': guest.checkin_time.isoformat()
                }
            })
            
        elif action == 'checkout':
            if not hasattr(guest, 'checkin_time') or not guest.checkin_time:
                return JsonResponse({'error': 'الضيف لم يسجل دخوله بعد'}, status=400)
            
            if hasattr(guest, 'checkout_time') and guest.checkout_time:
                return JsonResponse({'error': 'الضيف قد سجل خروجه بالفعل'}, status=400)
            
            guest.checkout_time = timezone.now()
            guest.save(update_fields=['checkout_time'])
            
            return JsonResponse({
                'success': True,
                'message': 'تم تسجيل الخروج بنجاح',
                'guest': {
                    'name': guest.name,
                    'code': guest.code,
                    'booking_id': guest.booking.id,
                    'property_name': guest.booking.property.name,
                    'checkin_time': guest.checkin_time.isoformat(),
                    'checkout_time': guest.checkout_time.isoformat()
                }
            })
        
    except BookingGuest.DoesNotExist:
        return JsonResponse({'error': 'الرمز غير موجود'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_guest_info(request, code):
    """الحصول على معلومات الضيف للعرض"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'غير مصرح'}, status=401)
    
    try:
        guest = BookingGuest.objects.select_related(
            'booking', 
            'booking__property', 
            'booking__user'
        ).get(code=code)
        
        # Debug info
        print(f"Guest: {guest.name}, Booking: {guest.booking.id}")
        print(f"Booking user: {guest.booking.user}")
        print(f"Property owner: {guest.booking.property.owner}")
        print(f"Current user: {request.user}")
        
        # Verify user owns the property OR is the booking user
        if guest.booking.user != request.user and guest.booking.property.owner != request.user:
            return JsonResponse({'error': 'غير مصرح بالوصول لهذا الحجز'}, status=403)
        
        return JsonResponse({
            'guest': {
                'name': guest.name,
                'code': guest.code,
                'serial': guest.serial,
                'booking_id': guest.booking.id,
                'property_name': guest.booking.property.name,
                'booking_status': guest.booking.status,
                'checkin_time': guest.checkin_time.isoformat() if hasattr(guest, 'checkin_time') and guest.checkin_time else None,
                'checkout_time': guest.checkout_time.isoformat() if hasattr(guest, 'checkout_time') and guest.checkout_time else None,
            }
        })
        
    except BookingGuest.DoesNotExist:
        return JsonResponse({'error': 'الرمز غير موجود'}, status=404)
