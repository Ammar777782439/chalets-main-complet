Role: You are an expert full-stack developer specializing in Python, Django, and modern frontend frameworks. Your task is to generate a complete, production-ready codebase for a web application based on the detailed requirements below.
Primary Objective: Generate the complete source code for a "Halls for Occasions and Parties Booking System." The system will be built using the Django framework for the backend and Tailwind CSS for all frontend styling. The entire user-facing interface, including all text, labels, and messages, must be exclusively in the Arabic language.
________________________________________
Core System Requirements
1. Technology Stack
•	Backend: Django
•	Frontend: Tailwind CSS
•	Database: Use Django's default SQLite for development, but structure the code to be easily portable to PostgreSQL for production.
•	Dependencies: django, pillow (for image handling), django-tailwind.
2. Project Structure
Generate a standard Django project structure named hall_system. Create the following apps within the project:
•	portfolio: To manage public-facing content like halls, offers, and contact information.
•	booking: To handle all booking and payment logic.
•	core: For base templates, static files, and project-wide configurations.
________________________________________
Feature Implementation Details
3. Portfolio App (portfolio)
This app manages the content that customers see before booking.
•	Models (models.py):
o	Hall:
	name (CharField, verbose_name="اسم القاعة")
	description (TextField, verbose_name="الوصف")
	capacity (PositiveIntegerField, verbose_name="السعة")
	price (DecimalField, verbose_name="السعر")
	main_image (ImageField, verbose_name="الصورة الرئيسية")
	is_available (BooleanField, default=True, verbose_name="متاحة للحجز؟")
o	Offer:
	title (CharField, verbose_name="عنوان العرض")
	description (TextField, verbose_name="تفاصيل العرض")
	hall (ForeignKey to Hall, verbose_name="القاعة")
	discount_percentage (PositiveIntegerField, verbose_name="نسبة الخصم")
o	GalleryImage:
	hall (ForeignKey to Hall, related_name='gallery_images', verbose_name="القاعة")
	image (ImageField, verbose_name="الصورة")
•	Views (views.py):
o	HomePageView: Displays featured halls and active offers.
o	HallListView: Shows all available halls in a card-based layout.
o	HallDetailView: Displays details for a single hall, including its image gallery, description, price, and a "Book Now" button.
o	ContactView: A static page with contact details (address, phone, map) and a simple contact form (Name, Phone, Message).
4. Booking and Payment App (booking)
This app handles the entire user booking and payment workflow.
•	Models (models.py):
o	PaymentProvider: Represents a payment service.
	name (CharField, verbose_name="اسم الوسيط")
	icon (ImageField, verbose_name="أيقونة الوسيط")
	account_number (CharField, verbose_name="رقم الحساب")
	is_active (BooleanField, default=True)
o	Booking: The core booking model.
	hall (ForeignKey to portfolio.Hall, verbose_name="القاعة المحجوزة")
	booking_date (DateField, verbose_name="تاريخ الحجز")
	customer_name (CharField, verbose_name="اسم العميل (رباعي)")
	customer_phone (CharField, verbose_name="رقم هاتف العميل")
	total_price (DecimalField, verbose_name="المبلغ الإجمالي")
	status (CharField with choices: 'Pending Confirmation', 'Confirmed', 'Cancelled', verbose_name="حالة الحجز")
	created_at (DateTimeField, auto_now_add=True)
o	Payment: Records the payment transaction details.
	booking (OneToOneField to Booking, verbose_name="الحجز")
	payment_method (CharField with choices: 'Bank Transfer', 'Cash', verbose_name="طريقة الدفع")
	provider (ForeignKey to PaymentProvider, null=True, blank=True, verbose_name="وسيط الدفع")
	transaction_id (CharField, null=True, blank=True, verbose_name="رقم عملية التحويل")
	payer_full_name (CharField, null=True, blank=True, verbose_name="اسم المحول (رباعي)")
	payer_phone_number (CharField, null=True, blank=True, verbose_name="رقم هاتف المحول")
	status (CharField with choices: 'Pending Review', 'Approved', 'Rejected', verbose_name="حالة الدفع")
	is_valid (BooleanField, default=False, verbose_name="تم التحقق؟")
•	Forms (forms.py):
o	BookingForm: A form to select the booking_date and enter customer_name and customer_phone. It must include validation to ensure the date is not in the past and the hall is not already booked for that date.
o	PaymentForm: A form for submitting bank transfer details: transaction_id, payer_full_name, and payer_phone_number. The payer_full_name field must validate that the input contains four distinct names.
•	Views (views.py):
o	CreateBookingView:
1.	Takes the Hall ID from the URL.
2.	Displays the BookingForm.
3.	On POST, validates the date and creates a Booking instance with status 'Pending Confirmation'.
4.	Redirects to the SelectPaymentMethodView.
o	SelectPaymentMethodView:
1.	Takes the Booking ID.
2.	Presents two options: "Pay via Bank Transfer" or "Pay Cash at Office".
o	BankTransferPaymentView:
1.	If "Bank Transfer" is selected, this view displays the list of active PaymentProviders (icon, name, account number).
2.	Shows the PaymentForm to submit transaction details.
3.	On submission, creates a Payment record linked to the booking with status 'Pending Review'.
o	CashPaymentConfirmationView:
1.	If "Cash" is selected, this view shows a confirmation message with office location and instructions, informing the user that their booking is held for 24 hours.
2.	Creates a Payment record with method 'Cash' and status 'Pending Review'.
o	BookingSuccessView: A final "thank you" page confirming the booking/payment submission is complete and under review.
5. Django Admin Interface
•	Register all models in their respective admin.py files.
•	For the Booking admin panel, display hall, booking_date, customer_name, and status in the list view. Add filters for status and booking_date.
•	For the Payment admin panel, display booking, payment_method, status, and is_valid.
o	Create a Django Admin Action named "Approve Payment" (def approve_payment(modeladmin, request, queryset)). This action should:
1.	Set the Payment status to 'Approved' and is_valid to True.
2.	Update the related Booking status to 'Confirmed'.
o	Create a Django Admin Action named "Reject Payment".
6. Frontend and UI (Tailwind CSS)
•	Ensure the base HTML template (core/base.html) is set up for Arabic: <html lang="ar" dir="rtl">.
•	Use Tailwind CSS for all styling to create a clean, modern, and fully responsive user interface.
•	Implement a clear visual hierarchy, intuitive navigation, and user-friendly forms.
•	The payment provider list must be displayed clearly with the icon, name, and account number for each provider.
________________________________________
Output Instructions
1.	Provide the complete code, organized file by file.
2.	Start with project setup: settings.py (ensure you add the new apps), urls.py (project-level), and the requirements.txt file.
3.	For each app, provide the code for models.py, admin.py, views.py, urls.py, forms.py (if applicable), and all required HTML templates in an app-specific templates directory.
4.	Include comments in the code to explain complex logic, especially for booking validation and payment status updates.
5.	Provide clear instructions on how to set up Tailwind CSS with this Django project.
	
