from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # User
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/password-change/', ChangePasswordView.as_view(), name='password_change'),
    path('user/delete-account/', DeleteAccountView.as_view(), name='delete_account'),

    # Properties
    path('properties/search/', PropertyViewSet.as_view({'get': 'list'}), name='property_search'),
    
    # Amenities
    path('amenities/', AmenityListView.as_view(), name='amenity_list'),

    # Bookings
    path('bookings/cancel/', BookingCancelView.as_view(), name='booking_cancel'),
    # Note: check-availability is handled by the router at bookings/check-availability/
    
    # Payments
    path('payments/providers/', PaymentProviderListView.as_view(), name='payment_providers'),
    path('payments/submit/', PaymentSubmitView.as_view(), name='payment_submit'),
    path('payments/status/', PaymentStatusView.as_view(), name='payment_status'),

    # Router
    path('', include(router.urls)),
]
