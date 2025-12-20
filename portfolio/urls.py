from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('properties/', views.PropertyListView.as_view(), name='property_list'),
    path('properties/<str:slug>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('owner/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('owner/properties/', views.OwnerPropertiesView.as_view(), name='owner_properties'),
    path('owner/bookings/', views.OwnerBookingsView.as_view(), name='owner_bookings'),
    path('owner/amenities/', views.OwnerAmenityListView.as_view(), name='owner_amenities'),
    path('owner/amenities/new/', views.OwnerAmenityCreateView.as_view(), name='owner_amenity_create'),
    path('owner/amenities/<int:pk>/edit/', views.OwnerAmenityUpdateView.as_view(), name='owner_amenity_edit'),
    path('owner/amenities/<int:pk>/delete/', views.OwnerAmenityDeleteView.as_view(), name='owner_amenity_delete'),
    path('owner/payment-providers/', views.OwnerPaymentProviderListView.as_view(), name='owner_payment_providers'),
    path('owner/payment-providers/create/', views.OwnerPaymentProviderCreateView.as_view(), name='owner_payment_provider_create'),
    path('owner/payment-providers/<int:pk>/edit/', views.OwnerPaymentProviderUpdateView.as_view(), name='owner_payment_provider_edit'),
    path('owner/payment-providers/<int:pk>/delete/', views.OwnerPaymentProviderDeleteView.as_view(), name='owner_payment_provider_delete'),
    path('owner/properties/create/', views.OwnerPropertyCreateView.as_view(), name='owner_property_create'),
    path('owner/properties/<str:slug>/edit/', views.OwnerPropertyUpdateView.as_view(), name='owner_property_edit'),
    path('owner/properties/<str:slug>/delete/', views.OwnerPropertyDeleteView.as_view(), name='owner_property_delete'),
    path('owner/properties/<str:slug>/gallery/add/', views.OwnerGalleryImageCreateView.as_view(), name='owner_property_gallery_add'),
    path('owner/bookings/<int:pk>/approve/', views.owner_booking_approve, name='owner_booking_approve'),
    path('owner/bookings/<int:pk>/cancel/', views.owner_booking_cancel, name='owner_booking_cancel'),
    path('owner/bookings/<int:pk>/', views.OwnerBookingDetailView.as_view(), name='owner_booking_detail'),
    path('owner/properties/<str:slug>/view/', views.OwnerPropertyDetailView.as_view(), name='owner_property_detail'),
]