import qrcode
import io
import base64
from django.conf import settings
from django.urls import reverse


def generate_qr_code_for_guest(guest, request=None):
    """
    Generate QR code for a guest containing verification information
    """
    # Create verification URL that can be scanned
    if request:
        verify_url = request.build_absolute_uri(f"/api/verify-guest/{guest.code}/")
    else:
        # Fallback for background tasks
        verify_url = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/api/verify-guest/{guest.code}/"
    
    # QR code data
    qr_data = {
        'code': guest.code,
        'guest_name': guest.name,
        'booking_id': guest.booking.id,
        'property': guest.booking.property.name if guest.booking.property else 'Unknown',
        'verify_url': verify_url
    }
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data as JSON string
    import json
    qr.add_data(json.dumps(qr_data, ensure_ascii=False))
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def generate_simple_qr_code(text):
    """
    Generate simple QR code for any text
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"
