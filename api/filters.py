import django_filters
from django.db.models import Q
from portfolio.models import Property
from booking.models import Booking

class PropertyFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price_per_day", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price_per_day", lookup_expr='lte')
    city = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    amenities = django_filters.CharFilter(method='filter_amenities')
    available_from = django_filters.DateTimeFilter(method='filter_availability')
    available_to = django_filters.DateTimeFilter(method='filter_availability')
    
    class Meta:
        model = Property
        fields = ['property_type', 'city', 'is_verified_by_platform', 'capacity']
        
    def filter_amenities(self, queryset, name, value):
        if not value:
            return queryset
        amenities = value.split(',')
        for amenity_id in amenities:
             if amenity_id.isdigit():
                 queryset = queryset.filter(amenities__id=amenity_id)
        return queryset

    def filter_availability(self, queryset, name, value):
        start = self.data.get('available_from')
        end = self.data.get('available_to')
        
        if not start or not end:
            return queryset
            
        if name == 'available_to': 
            # prevent running twice, run only when available_from is processed? 
            # or just run it. The logic below handles idempotency effectively if structured right,
            # but filtering twice is wasteful. 
            # actually django-filter runs method for each field.
            # I can just do it once if I check which field triggered it.
            return queryset

        # Logic: Exclude properties that have overlapping bookings
        
        # We need to parse start/end strings to datetime if they are strings (self.data has raw strings usually)
        # But 'value' passed to this method is already cleaned by the field (DateTimeFilter).
        
        # But wait, I need the OTHER value. 'available_to'.
        # self.form.cleaned_data might have it?
        
        # easier: just use self.request if available? No.
        # self.data is the raw data.
        
        # Let's try to get cleaned data if possible, or parse again.
        
        # Actually, let's just use the raw data from self.data and be careful.
        
        start_str = self.data.get('available_from')
        end_str = self.data.get('available_to')
        
        if not start_str or not end_str:
            return queryset
            
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        
        start_dt = parse_datetime(start_str)
        end_dt = parse_datetime(end_str)
        
        if not start_dt or not end_dt:
            return queryset
            
        if timezone.is_naive(start_dt):
            start_dt = timezone.make_aware(start_dt)
        if timezone.is_naive(end_dt):
            end_dt = timezone.make_aware(end_dt)
            
        qs = Booking.objects.filter(status__in=['pending', 'confirmed'])
        
        # Overlap logic from services.py
        overlap_q = Q(
            start_datetime__isnull=False,
            end_datetime__isnull=False,
            start_datetime__lt=end_dt,
            end_datetime__gt=start_dt
        )
        
        legacy_q = Q(start_datetime__isnull=True, end_datetime__isnull=True) & (
            Q(booking_date=start_dt.date()) | Q(booking_date=end_dt.date())
        )
        
        conflicting_bookings = qs.filter(overlap_q | legacy_q)
        booked_property_ids = conflicting_bookings.values_list('property_id', flat=True)
        
        return queryset.exclude(id__in=booked_property_ids)
