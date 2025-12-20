from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from portfolio.models import Property
from .models import Booking, Payment, PaymentProvider, BookingGuest
from .forms import PropertyBookingForm, PaymentForm
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.utils import timezone
import secrets
import string
from django.db.models import Q


class CreatePropertyBookingView(LoginRequiredMixin, TemplateView):
    """إنشاء حجز جديد لعقار (شاليه/استراحة/حديقة)"""
    template_name = 'booking/create_property_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_id = kwargs.get('property_id')
        context['property'] = get_object_or_404(Property, pk=property_id)
        initial_data = {
            'customer_name': self.request.user.userprofile.full_name if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.full_name else '',
            'customer_phone': self.request.user.userprofile.phone_number if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.phone_number else ''
        }
        # Prefill from GET params
        bt = self.request.GET.get('booking_type')
        if bt:
            initial_data['booking_type'] = bt
        start_str = self.request.GET.get('start') or self.request.GET.get('start_datetime')
        end_str = self.request.GET.get('end') or self.request.GET.get('end_datetime')
        def parse_dt(val):
            try:
                dt = datetime.fromisoformat(val)
                if timezone.is_naive(dt):
                    try:
                        dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    except Exception:
                        pass
                return dt
            except Exception:
                return None
        if start_str:
            dt = parse_dt(start_str)
            if dt:
                initial_data['start_datetime'] = dt
        if end_str:
            dt = parse_dt(end_str)
            if dt:
                initial_data['end_datetime'] = dt
        context['form'] = PropertyBookingForm(property=context['property'], initial=initial_data)
        return context

    def post(self, request, *args, **kwargs):
        property_id = kwargs.get('property_id')
        prop = get_object_or_404(Property, pk=property_id)
        form = PropertyBookingForm(request.POST, property=prop)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.property = prop
            booking.user = request.user
            # Backfill legacy booking_date for compatibility
            if booking.start_datetime:
                booking.booking_date = booking.start_datetime.date()
            # Compute total based on booking_type
            total = form.compute_total_price()
            if total is None:
                total = prop.price_per_day or 0
            booking.total_price = total
            booking.status = 'pending'
            booking.save()

            # Save guests (if provided)
            guest_text = form.cleaned_data.get('guest_names') or ''
            lines = [ln.strip() for ln in guest_text.splitlines() if ln and ln.strip()]
            if lines:
                # generate unique code per guest within this booking
                def gen_code():
                    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
                    return ''.join(secrets.choice(alphabet) for _ in range(6))
                existing_codes = set()
                serial = 1
                for name in lines:
                    code = gen_code()
                    # ensure uniqueness per booking
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

            messages.success(request, 'تم إنشاء الحجز بنجاح. يرجى اختيار طريقة الدفع.')
            return redirect('booking:select_payment_method', booking_id=booking.id)

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


class SelectPaymentMethodView(LoginRequiredMixin, TemplateView):
    """اختيار طريقة الدفع للحجز"""
    template_name = 'booking/select_payment_method.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = kwargs.get('booking_id')
        context['booking'] = get_object_or_404(Booking, pk=booking_id, status='pending')
        # Deposit info
        dep_percent = getattr(settings, 'DEPOSIT_PERCENT', 0)
        total = context['booking'].total_price or Decimal('0')
        deposit_amount = (Decimal(dep_percent) / Decimal('100')) * total
        deposit_amount = deposit_amount.quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        context['deposit_percent'] = dep_percent
        context['deposit_amount'] = deposit_amount
        balance_amount = (total - deposit_amount).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        context['balance_amount'] = balance_amount
        return context
    
    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, pk=booking_id, status='pending')
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'bank_transfer':
            booking.payment_method = 'bank_transfer'
            booking.payment_status = 'pending'
            booking.save(update_fields=['payment_method', 'payment_status'])
            return redirect('booking:bank_transfer_payment', booking_id=booking.id)
        elif payment_method == 'cash':
            # Cash requires deposit; set payment status accordingly
            booking.payment_method = 'cash'
            # Compute and store deposit amount
            dep_percent = getattr(settings, 'DEPOSIT_PERCENT', 0)
            total = booking.total_price or Decimal('0')
            deposit_amount = (Decimal(dep_percent) / Decimal('100')) * total
            deposit_amount = deposit_amount.quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
            booking.deposit_amount = deposit_amount
            booking.payment_status = 'cash_on_arrival'
            booking.save(update_fields=['payment_method', 'payment_status', 'deposit_amount'])
            return redirect('booking:cash_payment_confirmation', booking_id=booking.id)
        elif payment_method == 'wallet_transfer':
            booking.payment_method = 'wallet_transfer'
            booking.payment_status = 'pending'
            booking.save(update_fields=['payment_method', 'payment_status'])
            return redirect('booking:bank_transfer_payment', booking_id=booking.id)
        else:
            messages.error(request, 'يرجى اختيار طريقة دفع صحيحة.')
            return redirect('booking:select_payment_method', booking_id=booking.id)


class BankTransferPaymentView(LoginRequiredMixin, TemplateView):
    """عرض تفاصيل التحويل البنكي وتسجيل بيانات الدفع"""
    template_name = 'booking/bank_transfer_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, pk=booking_id, status='pending')
        context['booking'] = booking
        owner = getattr(getattr(booking, 'property', None), 'owner', None)
        qs = PaymentProvider.objects.filter(is_active=True)
        if owner is not None:
            qs = qs.filter(owner=owner)
        else:
            qs = PaymentProvider.objects.none()
        context['payment_providers'] = qs
        context['form'] = PaymentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, pk=booking_id, status='pending')
        provider_id = request.POST.get('provider_id')
        
        if not provider_id:
            messages.error(request, 'يرجى اختيار وسيط الدفع.')
            return redirect('booking:bank_transfer_payment', booking_id=booking.id)
        
        # Ensure selected provider belongs to the booking's owner (or is global)
        owner = getattr(getattr(booking, 'property', None), 'owner', None)
        provider_qs = PaymentProvider.objects.filter(pk=provider_id, is_active=True)
        if owner is not None:
            provider_qs = provider_qs.filter(owner=owner)
        else:
            provider_qs = PaymentProvider.objects.none()
        provider = get_object_or_404(provider_qs)
        form = PaymentForm(request.POST)
        
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.payment_method = 'bank_transfer'
            payment.provider = provider
            payment.status = 'pending'
            payment.is_valid = False
            payment.save()
            
            messages.success(request, 'تم تسجيل بيانات التحويل بنجاح. سيتم مراجعة الدفع والتأكيد خلال 24 ساعة.')
            return redirect('booking:booking_success', booking_id=booking.id)
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        context['selected_provider_id'] = int(provider_id) if provider_id else None
        return render(request, self.template_name, context)


class CashPaymentConfirmationView(LoginRequiredMixin, TemplateView):
    """تأكيد الدفع النقدي في المكتب"""
    template_name = 'booking/cash_payment_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = kwargs.get('booking_id')
        context['booking'] = get_object_or_404(Booking, pk=booking_id, status='pending')
        # Deposit info
        dep_percent = getattr(settings, 'DEPOSIT_PERCENT', 0)
        total = context['booking'].total_price or Decimal('0')
        deposit_amount = context['booking'].deposit_amount or (Decimal(dep_percent) / Decimal('100')) * total
        deposit_amount = Decimal(deposit_amount).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        context['deposit_percent'] = dep_percent
        context['deposit_amount'] = deposit_amount
        context['balance_amount'] = (total - deposit_amount) if total else Decimal('0')
        return context
    
    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, pk=booking_id, status='pending')
        
        # إنشاء سجل دفع نقدي
        payment = Payment.objects.create(
            booking=booking,
            payment_method='cash',
            status='pending',
            is_valid=False
        )
        
        messages.success(request, 'تم تسجيل طلب الدفع النقدي. يرجى زيارة المكتب خلال 24 ساعة لإتمام الدفع.')
        return redirect('booking:booking_success', booking_id=booking.id)


class BookingSuccessView(LoginRequiredMixin, TemplateView):
    """صفحة تأكيد نجاح الحجز والدفع"""
    template_name = 'booking/booking_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = kwargs.get('booking_id')
        context['booking'] = get_object_or_404(Booking, pk=booking_id)
        try:
            context['payment'] = Payment.objects.get(booking=context['booking'])
        except Payment.DoesNotExist:
            context['payment'] = None
        return context


class BookingGuestsView(LoginRequiredMixin, TemplateView):
    """عرض وطباعة قائمة الضيوف للعميل"""
    template_name = 'booking/guest_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = kwargs.get('booking_id')
        booking = get_object_or_404(Booking, pk=booking_id, user=self.request.user)
        context['booking'] = booking
        context['guests'] = booking.guests.all().order_by('serial')
        context['can_download'] = booking.status == 'confirmed'
        return context


@login_required
def booking_guests_csv(request, booking_id: int):
    """تنزيل قائمة الضيوف بصيغة CSV (متاح فقط للحجوزات المؤكدة)"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.status != 'confirmed':
        messages.error(request, 'لا يمكن تنزيل قائمة الضيوف قبل تأكيد الحجز.')
        return redirect('booking:guest_list', booking_id=booking.id)

    # Prepare CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="booking_{booking.id}_guests.csv"'

    # Write BOM for Excel Arabic compatibility
    response.write('\ufeff')

    import csv
    writer = csv.writer(response)
    writer.writerow(['Serial', 'Name', 'Code'])
    for g in booking.guests.all().order_by('serial'):
        writer.writerow([g.serial, g.name, g.code])
    return response
