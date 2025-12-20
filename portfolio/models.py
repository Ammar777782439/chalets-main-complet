from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from django.db.models import Q
import uuid


class GalleryImage(models.Model):
    """صور المعرض للعقارات"""
    property = models.ForeignKey(
        'Property',
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name="العقار",
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to='gallery/', verbose_name="الصورة")
    caption = models.CharField(max_length=200, blank=True, verbose_name="وصف الصورة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "صورة معرض"
        verbose_name_plural = "صور المعرض"
        ordering = ['-created_at']

    def __str__(self):
        return f"صورة {self.property.name} - {self.id}"


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=100, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='amenities',
        verbose_name="المالك",
    )

    class Meta:
        verbose_name = "ميزة"
        verbose_name_plural = "المزايا"
        ordering = ['name']
        constraints = [
            # لكل مالك، اسم الميزة يجب أن يكون فريداً
            models.UniqueConstraint(fields=['owner', 'name'], name='unique_amenity_per_owner'),
            # للميزات العامة (owner=null)، اسم الميزة يجب أن يكون فريداً
            models.UniqueConstraint(fields=['name'], condition=Q(owner__isnull=True), name='unique_global_amenity_name'),
        ]

    def __str__(self):
        return self.name


class Property(models.Model):
    PROPERTY_TYPES = [
        ('chalet', 'Chalet'),
        ('garden', 'Garden'),
        ('istiraha', 'Istiraha'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    main_image = models.ImageField(upload_to='properties/', verbose_name="الصورة الرئيسية")
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='chalet')

    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_half_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_price_negotiable = models.BooleanField(default=False)

    amenities = models.ManyToManyField('Amenity', blank=True)
    city = models.CharField(max_length=100, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_properties',
        verbose_name="المالك",
    )

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        verbose_name="خط العرض",
        help_text="خط العرض للموقع على الخريطة"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        verbose_name="خط الطول",
        help_text="خط الطول للموقع على الخريطة"
    )
    address = models.TextField(blank=True, verbose_name="العنوان")

    privacy_rating = models.PositiveSmallIntegerField(default=3)
    is_verified_by_platform = models.BooleanField(default=False)
    checkin_time = models.TimeField(null=True, blank=True)
    checkout_time = models.TimeField(null=True, blank=True)

    slug = models.SlugField(
        max_length=200,
        unique=True,
        allow_unicode=True,
        blank=True,
        verbose_name="رابط العقار (Slug)",
        help_text="يتم إنشاؤه تلقائياً من الاسم"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "عقار"
        verbose_name_plural = "العقارات"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class PropertyReview(models.Model):
    RATING_CHOICES = [
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='property_reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تقييم عقار"
        verbose_name_plural = "تقييمات العقارات"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['property', 'user'], condition=Q(user__isnull=False), name='unique_property_review_per_user')
        ]

    def __str__(self):
        uname = self.user.username if self.user and hasattr(self.user, 'username') else 'مستخدم'
        return f"{self.property.name} - {uname} ({self.rating})"
