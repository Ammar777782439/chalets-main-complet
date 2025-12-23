from django.urls import path
from . import views
from . import views_scan

app_name = 'booking'

urlpatterns = [
    path('create-property/<int:property_id>/', views.CreatePropertyBookingView.as_view(), name='create_property_booking'),
    path('payment-method/<int:booking_id>/', views.SelectPaymentMethodView.as_view(), name='select_payment_method'),
    path('bank-transfer/<int:booking_id>/', views.BankTransferPaymentView.as_view(), name='bank_transfer_payment'),
    path('cash-payment/<int:booking_id>/', views.CashPaymentConfirmationView.as_view(), name='cash_payment_confirmation'),
    path('success/<int:booking_id>/', views.BookingSuccessView.as_view(), name='booking_success'),
    path('<int:booking_id>/guests/', views.BookingGuestsView.as_view(), name='guest_list'),
    path('<int:booking_id>/guests.csv', views.booking_guests_csv, name='guest_list_csv'),
    
    # QR Scanner
    path('scanner/', views_scan.QRScannerView.as_view(), name='qr_scanner'),
]