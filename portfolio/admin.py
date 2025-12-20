from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryImage, Amenity, Property, PropertyReview
from .forms import PropertyAdminForm


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
    search_fields = ('name',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    form = PropertyAdminForm
    list_display = (
        'name', 'property_type', 'city', 'owner', 'main_image_preview',
        'price_per_hour', 'price_half_day', 'price_per_day',
        'is_verified_by_platform', 'created_at'
    )
    list_filter = ('property_type', 'city', 'owner', 'is_verified_by_platform', 'privacy_rating', 'created_at')
    search_fields = ('name', 'description', 'city', 'owner__username', 'owner__email')
    filter_horizontal = ('amenities',)
    readonly_fields = ('main_image_preview',)
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'slug', 'description', 'property_type', 'owner', 'main_image', 'main_image_preview')
        }),
        ('التسعير', {
            'fields': ('price_per_hour', 'price_half_day', 'price_per_day', 'is_price_negotiable')
        }),
        ('المزايا', {
            'fields': ('amenities', 'privacy_rating', 'is_verified_by_platform', 'capacity')
        }),
        ('الموقع', {
            'fields': ('city', 'location'),
            'description': 'استخدم الخريطة أدناه لتحديد موقع العقار بدقة'
        }),
        ('التوقيت', {
            'fields': ('checkin_time', 'checkout_time')
        }),
    )

    class Media:
        css = {
            'all': (
                'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            )
        }
        js = (
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
        )

    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;"/>',
                obj.main_image.url
            )
        return format_html('<div style="width: 60px; height: 60px; background: #f3f4f6; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #9ca3af; font-size: 12px;">لا توجد صورة</div>')

    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


## Removed Offer admin (legacy)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """إدارة صور المعرض للعقارات"""
    list_display = ('property', 'image_preview', 'created_at')
    list_filter = ('property', 'created_at')
    search_fields = ('property__name',)
    ordering = ('-created_at',)
    fields = ('property', 'image', 'image_preview')
    readonly_fields = ('image_preview',)
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"/>', obj.image.url)
        return format_html('<div style="width: 80px; height: 80px; background: #f3f4f6; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #9ca3af; font-size: 12px;">لا توجد صورة</div>')
    image_preview.short_description = 'معاينة الصورة'


## Removed Testimonial admin (legacy)


@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at', 'property')
    search_fields = ('property__name', 'user__username', 'comment')
    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description="اعتماد التقييمات المحددة")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="رفض التقييمات المحددة")
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
