from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Exists, OuterRef, Avg
import math
from .models import Property, Amenity, PropertyReview, GalleryImage


class OwnerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and (user.is_superuser or (hasattr(user, 'userprofile') and getattr(user.userprofile, 'is_owner', False))):
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'لا تملك صلاحية الوصول إلى لوحة المالك.')
        return redirect('portfolio:home')
from .forms import ContactForm, PropertySearchForm, PropertyReviewForm, OwnerPropertyForm
from booking.models import Booking, PaymentProvider


class HomePageView(TemplateView):
    """عرض الصفحة الرئيسية مع العقارات المميزة"""
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # عرض أول 6 عقارات موثقة
        context['featured_properties'] = Property.objects.filter(is_verified_by_platform=True)[:6]
        
        # إحصائيات الموقع
        context['stats'] = {
            'total_properties': Property.objects.count(),
            'verified_properties': Property.objects.filter(is_verified_by_platform=True).count(),
            'total_bookings': Booking.objects.filter(status='confirmed').count(),
            'happy_customers': Booking.objects.filter(status='confirmed').values('customer_phone').distinct().count(),
        }
        return context


class AboutView(TemplateView):
    """عرض صفحة من نحن"""
    template_name = 'portfolio/about.html'


class ContactView(TemplateView):
    """صفحة ثابتة مع تفاصيل الاتصال ونموذج اتصال بسيط"""
    template_name = 'portfolio/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # في التطبيق الحقيقي، يمكن حفظ الرسالة في قاعدة البيانات أو إرسالها بالبريد الإلكتروني
            messages.success(request, 'تم إرسال رسالتك بنجاح. سنتواصل معك قريباً.')
            return HttpResponseRedirect(reverse('portfolio:contact'))
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج.')
            context = self.get_context_data(**kwargs)
            context['contact_form'] = form
            return render(request, self.template_name, context)


class OwnerDashboardView(OwnerRequiredMixin, TemplateView):
    template_name = 'portfolio/owner/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        props = Property.objects.filter(owner=user)
        bookings = Booking.objects.filter(property__owner=user)
        stats = {
            'properties_count': props.count(),
            'bookings_count': bookings.count(),
            'pending_count': bookings.filter(status='pending').count(),
            'confirmed_count': bookings.filter(status='confirmed').count(),
            'cancelled_count': bookings.filter(status='cancelled').count(),
            'total_revenue': bookings.filter(status='confirmed').aggregate(total=Sum('total_price'))['total'] or 0,
        }
        context['stats'] = stats
        context['recent_bookings'] = bookings.select_related('property').order_by('-created_at')[:10]
        context['properties'] = props.order_by('-created_at')[:10]
        return context


class OwnerPropertiesView(OwnerRequiredMixin, ListView):
    model = Property
    template_name = 'portfolio/owner/properties.html'
    context_object_name = 'properties'
    paginate_by = 20

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user).order_by('-created_at')


class OwnerBookingsView(OwnerRequiredMixin, ListView):
    model = Booking
    template_name = 'portfolio/owner/bookings.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        qs = Booking.objects.filter(property__owner=self.request.user).select_related('property').order_by('-created_at')
        status = self.request.GET.get('status')
        if status in {'pending', 'confirmed', 'cancelled'}:
            qs = qs.filter(status=status)
        return qs


class OwnerPaymentProviderListView(OwnerRequiredMixin, ListView):
    model = PaymentProvider
    template_name = 'portfolio/owner/payment_providers_list.html'
    context_object_name = 'providers'

    def get_queryset(self):
        return PaymentProvider.objects.filter(owner=self.request.user).order_by('-created_at')


class OwnerPaymentProviderCreateView(OwnerRequiredMixin, CreateView):
    model = PaymentProvider
    template_name = 'portfolio/owner/payment_provider_form.html'
    fields = ['name', 'icon', 'account_number', 'provider_type', 'is_active']
    success_url = reverse_lazy('portfolio:owner_payment_providers')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        messages.success(self.request, 'تم إضافة وسيط الدفع بنجاح')
        return super().form_valid(form)


class OwnerPaymentProviderUpdateView(OwnerRequiredMixin, UpdateView):
    model = PaymentProvider
    template_name = 'portfolio/owner/payment_provider_form.html'
    fields = ['name', 'icon', 'account_number', 'provider_type', 'is_active']
    context_object_name = 'provider'
    success_url = reverse_lazy('portfolio:owner_payment_providers')

    def get_queryset(self):
        return PaymentProvider.objects.filter(owner=self.request.user)


class OwnerAmenityListView(OwnerRequiredMixin, ListView):
    model = Amenity
    template_name = 'portfolio/owner/amenities_list.html'
    context_object_name = 'amenities'

    def get_queryset(self):
        return Amenity.objects.filter(owner=self.request.user).order_by('name')


class OwnerAmenityCreateView(OwnerRequiredMixin, CreateView):
    model = Amenity
    template_name = 'portfolio/owner/amenity_form.html'
    fields = ['name', 'icon_class']
    success_url = reverse_lazy('portfolio:owner_amenities')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        messages.success(self.request, 'تمت إضافة الميزة بنجاح')
        return super().form_valid(form)


class OwnerAmenityUpdateView(OwnerRequiredMixin, UpdateView):
    model = Amenity
    template_name = 'portfolio/owner/amenity_form.html'
    fields = ['name', 'icon_class']
    context_object_name = 'amenity'
    success_url = reverse_lazy('portfolio:owner_amenities')

    def get_queryset(self):
        return Amenity.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الميزة بنجاح')
        return super().form_valid(form)


class OwnerAmenityDeleteView(OwnerRequiredMixin, DeleteView):
    model = Amenity
    template_name = 'portfolio/owner/amenity_confirm_delete.html'
    context_object_name = 'amenity'
    success_url = reverse_lazy('portfolio:owner_amenities')

    def get_queryset(self):
        return Amenity.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث وسيط الدفع بنجاح')
        return super().form_valid(form)


class OwnerPaymentProviderDeleteView(OwnerRequiredMixin, DeleteView):
    model = PaymentProvider
    template_name = 'portfolio/owner/payment_provider_confirm_delete.html'
    context_object_name = 'provider'
    success_url = reverse_lazy('portfolio:owner_payment_providers')

    def get_queryset(self):
        return PaymentProvider.objects.filter(owner=self.request.user)

class OwnerBookingDetailView(OwnerRequiredMixin, DetailView):
    model = Booking
    template_name = 'portfolio/owner/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return Booking.objects.select_related('property').filter(property__owner=self.request.user)


class OwnerPropertyDetailView(OwnerRequiredMixin, DetailView):
    model = Property
    template_name = 'portfolio/owner/property_detail.html'
    context_object_name = 'property'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user).prefetch_related('amenities', 'gallery_images', 'reviews', 'booking_set')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prop = self.object
        context['total_bookings'] = prop.booking_set.count()
        context['confirmed_bookings'] = prop.booking_set.filter(status='confirmed').count()
        context['pending_bookings'] = prop.booking_set.filter(status='pending').count()
        
        # Reviews stats
        approved_reviews = prop.reviews.filter(is_approved=True)
        context['reviews_count'] = approved_reviews.count()
        context['avg_rating'] = approved_reviews.aggregate(avg=Avg('rating'))['avg']
        
        return context


@login_required
@require_POST
def owner_booking_approve(request, pk):
    user = request.user
    if not (user.is_superuser or (hasattr(user, 'userprofile') and getattr(user.userprofile, 'is_owner', False))):
        messages.error(request, 'لا تملك صلاحية الوصول إلى لوحة المالك.')
        return redirect('portfolio:home')
    booking = get_object_or_404(Booking.objects.select_related('property'), pk=pk, property__owner=request.user)
    if booking.status != 'confirmed':
        booking.status = 'confirmed'
        booking.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'تم اعتماد الحجز بنجاح.')
    return redirect('portfolio:owner_bookings')


@login_required
@require_POST
def owner_booking_cancel(request, pk):
    user = request.user
    if not (user.is_superuser or (hasattr(user, 'userprofile') and getattr(user.userprofile, 'is_owner', False))):
        messages.error(request, 'لا تملك صلاحية الوصول إلى لوحة المالك.')
        return redirect('portfolio:home')
    booking = get_object_or_404(Booking.objects.select_related('property'), pk=pk, property__owner=request.user)
    if booking.status != 'cancelled':
        booking.status = 'cancelled'
        booking.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'تم إلغاء الحجز.')
    return redirect('portfolio:owner_bookings')


class OwnerPropertyCreateView(OwnerRequiredMixin, CreateView):
    model = Property
    template_name = 'portfolio/owner/property_form.html'
    form_class = OwnerPropertyForm
    success_url = reverse_lazy('portfolio:owner_properties')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        form.save_m2m()
        messages.success(self.request, 'تم إنشاء العقار بنجاح')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        # عند إنشاء عقار جديد، أظهر للمالك مزاياه الخاصة فقط
        kwargs['owner_only'] = True
        return kwargs


class OwnerPropertyUpdateView(OwnerRequiredMixin, UpdateView):
    model = Property
    template_name = 'portfolio/owner/property_form.html'
    context_object_name = 'property'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = OwnerPropertyForm
    success_url = reverse_lazy('portfolio:owner_properties')

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث العقار بنجاح')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class OwnerPropertyDeleteView(OwnerRequiredMixin, DeleteView):
    model = Property
    template_name = 'portfolio/owner/property_confirm_delete.html'
    context_object_name = 'property'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('portfolio:owner_properties')

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)


class OwnerGalleryImageCreateView(OwnerRequiredMixin, CreateView):
    model = GalleryImage
    template_name = 'portfolio/owner/gallery_add.html'
    fields = ['image', 'caption']

    def dispatch(self, request, *args, **kwargs):
        self.property_obj = get_object_or_404(Property, slug=kwargs.get('slug'), owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        img = form.save(commit=False)
        img.property = self.property_obj
        img.save()
        messages.success(self.request, 'تم إضافة الصورة بنجاح')
        return HttpResponseRedirect(reverse('portfolio:owner_properties'))


class PropertyListView(ListView):
    """قائمة العقارات (شاليهات/حدائق/استراحات) مع فلاتر وفلترة التوفر بالزمن"""
    model = Property
    template_name = 'portfolio/property_list.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        queryset = Property.objects.all()
        form = PropertySearchForm(self.request.GET)
        self._form = form

        if form.is_valid():
            cd = form.cleaned_data

            search = cd.get('search')
            if search:
                queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

            city = cd.get('city')
            if city:
                queryset = queryset.filter(city=city)

            if cd.get('is_verified_by_platform'):
                queryset = queryset.filter(is_verified_by_platform=True)

            min_privacy = cd.get('min_privacy')
            if min_privacy:
                queryset = queryset.filter(privacy_rating__gte=min_privacy)

            min_capacity = cd.get('min_capacity')
            if min_capacity:
                queryset = queryset.filter(capacity__gte=min_capacity)

            max_capacity = cd.get('max_capacity')
            if max_capacity:
                queryset = queryset.filter(capacity__lte=max_capacity)

            # Price filters based on booking type
            booking_type = cd.get('booking_type')
            price_field = 'price_per_day'
            if booking_type == 'hourly':
                price_field = 'price_per_hour'
            elif booking_type == 'half_day':
                price_field = 'price_half_day'
            elif booking_type in ('full_day', 'overnight'):
                price_field = 'price_per_day'

            min_price = cd.get('min_price')
            if min_price is not None and min_price != '':
                queryset = queryset.filter(**{f'{price_field}__gte': min_price})

            max_price = cd.get('max_price')
            if max_price is not None and max_price != '':
                queryset = queryset.filter(**{f'{price_field}__lte': max_price})

            # Amenities: require all selected
            amenities = cd.get('amenities')
            if amenities:
                queryset = queryset.filter(amenities__in=amenities)
                queryset = queryset.annotate(match_count=Count('amenities', filter=Q(amenities__in=amenities), distinct=True))
                queryset = queryset.filter(match_count=amenities.count())

            # Timeslot availability filter
            start = cd.get('start_datetime')
            end = cd.get('end_datetime')
            if start and end:
                overlap = Booking.objects.filter(property=OuterRef('pk'), status__in=['pending', 'confirmed']).filter(
                    start_datetime__lt=end, end_datetime__gt=start
                )
                queryset = queryset.annotate(has_overlap=Exists(overlap)).filter(has_overlap=False)

            # Radius filter around city center (approx bounding box)
            radius_km = cd.get('radius_km')
            if city and radius_km:
                centers = {
                    "Sana'a": (15.3694, 44.1910),
                    "Ibb": (13.9667, 44.1833),
                    "Aden": (12.7794, 45.0367),
                    "Taiz": (13.5795, 44.0209),
                    "Hodeidah": (14.7979, 42.9545),
                }
                if city in centers:
                    lat0, lon0 = centers[city]
                    deg_lat = float(radius_km) / 111.0
                    # Avoid division by zero at poles
                    cos_lat = max(0.000001, math.cos(math.radians(lat0)))
                    deg_lon = float(radius_km) / (111.0 * cos_lat)
                    queryset = queryset.exclude(latitude__isnull=True, longitude__isnull=True)
                    queryset = queryset.filter(
                        latitude__gte=lat0 - deg_lat,
                        latitude__lte=lat0 + deg_lat,
                        longitude__gte=lon0 - deg_lon,
                        longitude__lte=lon0 + deg_lon,
                    )

            # Ordering
            ordering = cd.get('ordering')
            # Annotate ratings (approved only)
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
                reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
            )
            if ordering:
                if ordering in ('price', '-price'):
                    field = price_field
                    if ordering.startswith('-'):
                        field = '-' + field
                elif ordering in ('rating', '-rating'):
                    # 'rating' = highest first, map to '-avg_rating'
                    field = '-avg_rating' if ordering == 'rating' else 'avg_rating'
                else:
                    field = ordering
                queryset = queryset.order_by(field)
            else:
                queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
                reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
            ).order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = getattr(self, '_form', PropertySearchForm(self.request.GET))
        context['current_search'] = self.request.GET.dict()
        context['properties_with_location'] = self.get_queryset().exclude(latitude__isnull=True, longitude__isnull=True)
        context['current_view'] = self.request.GET.get('view', 'list')
        return context


class PropertyDetailView(DetailView):
    model = Property
    template_name = 'portfolio/property_detail.html'
    context_object_name = 'property'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Property.objects.prefetch_related('gallery_images', 'amenities', 'reviews')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prop = self.object
        approved = prop.reviews.filter(is_approved=True)
        context['reviews'] = approved.order_by('-created_at')[:20]
        context['avg_rating'] = approved.aggregate(avg=Avg('rating'))['avg']
        context['reviews_count'] = approved.count()
        user_review = None
        if self.request.user.is_authenticated:
            user_review = PropertyReview.objects.filter(property=prop, user=self.request.user).first()
        context['user_review'] = user_review
        context['review_form'] = PropertyReviewForm(instance=user_review) if user_review else PropertyReviewForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            messages.error(request, 'يجب تسجيل الدخول لإضافة تقييم.')
            return HttpResponseRedirect(reverse('accounts:login') + f"?next={request.path}")
        form = PropertyReviewForm(request.POST)
        if form.is_valid():
            # Update existing review if present, else create new
            review = PropertyReview.objects.filter(property=self.object, user=request.user).first()
            if review:
                review.rating = form.cleaned_data['rating']
                review.comment = form.cleaned_data['comment']
                review.is_approved = False  # re-moderate
                review.save()
                messages.success(request, 'تم تحديث تقييمك وسيتم نشره بعد الموافقة.')
            else:
                review = form.save(commit=False)
                review.property = self.object
                review.user = request.user
                review.is_approved = False
                review.save()
                messages.success(request, 'تم إرسال تقييمك للمراجعة. سيتم نشره بعد الموافقة.')
            return HttpResponseRedirect(self.object.get_absolute_url() if hasattr(self.object, 'get_absolute_url') else request.path)
        context = self.get_context_data()
        context['review_form'] = form
        return render(request, self.template_name, context)
