from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import UserProfile
from portfolio.models import Property, Amenity, PropertyReview
from booking.models import Booking, PaymentProvider, Payment
from django.utils import timezone
from datetime import timedelta

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'full_name': 'Test User Name One',
            'phone_number': '123456789'
        }

    def test_register(self):
        response = self.client.post(self.register_url, self.user_data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='testuser').exists())

    def test_login(self):
        self.client.post(self.register_url, self.user_data, follow=True)
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('user_profile')

    def test_get_profile(self):
        response = self.client.get(self.profile_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile(self):
        data = {'full_name': 'New Name Test One'}
        response = self.client.patch(self.profile_url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'New Name Test One')

    def test_change_password(self):
        url = reverse('password_change')
        data = {'old_password': 'password123', 'new_password': 'newpassword123'}
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

class PropertyTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='password')
        self.client.force_authenticate(user=self.user)
        
        # Create multiple properties for comprehensive testing
        self.property1 = Property.objects.create(
            name='Test Property Riyadh',
            description='Beautiful property in Riyadh',
            city='Riyadh',
            price_per_day=100,
            capacity=5,
            owner=self.user,
            is_verified_by_platform=True,
            property_type='chalet'
        )
        
        self.property2 = Property.objects.create(
            name='Test Property Jeddah',
            description='Amazing property in Jeddah',
            city='Jeddah',
            price_per_day=200,
            capacity=10,
            owner=self.user,
            is_verified_by_platform=True,
            property_type='garden'
        )
        
        self.property3 = Property.objects.create(
            name='Budget Property Riyadh',
            description='Affordable property in Riyadh',
            city='Riyadh',
            price_per_day=50,
            capacity=3,
            owner=self.user,
            is_verified_by_platform=False,
            property_type='istiraha'
        )
        
        self.property4 = Property.objects.create(
            name='Luxury Property Dammam',
            description='High-end property in Dammam',
            city='Dammam',
            price_per_day=500,
            capacity=20,
            owner=self.user,
            is_verified_by_platform=True,
            property_type='chalet'
        )
        
        # Create gallery images for property1
        from portfolio.models import GalleryImage
        self.gallery1 = GalleryImage.objects.create(
            property=self.property1,
            caption='Main view'
        )
        self.gallery2 = GalleryImage.objects.create(
            property=self.property1,
            caption='Side view'
        )
        
        self.list_url = reverse('property-list')

    def test_list_properties(self):
        """Test basic property listing"""
        response = self.client.get(self.list_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_filter_by_city(self):
        """Test filtering properties by city"""
        response = self.client.get(self.list_url, {'city': 'Riyadh'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        response = self.client.get(self.list_url, {'city': 'Jeddah'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        response = self.client.get(self.list_url, {'city': 'Mecca'}, follow=True)
        self.assertEqual(len(response.data['results']), 0)

    def test_filter_by_price_range(self):
        """Test filtering properties by price range"""
        # Filter min price
        response = self.client.get(self.list_url, {'min_price': 100}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Filter max price
        response = self.client.get(self.list_url, {'max_price': 100}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Filter price range (min and max)
        response = self.client.get(self.list_url, {'min_price': 100, 'max_price': 200}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_capacity(self):
        """Test filtering properties by capacity"""
        response = self.client.get(self.list_url, {'capacity': 5}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Property Riyadh')

    def test_advanced_filtering(self):
        """Test combining multiple filters"""
        # Filter by city and price range
        response = self.client.get(self.list_url, {
            'city': 'Riyadh',
            'min_price': 50,
            'max_price': 100
        }, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Filter by city, price, capacity, and verification status
        response = self.client.get(self.list_url, {
            'city': 'Riyadh',
            'min_price': 50,
            'max_price': 150,
            'is_verified_by_platform': True
        }, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Property Riyadh')

    def test_search_by_name(self):
        """Test searching properties by name"""
        response = self.client.get(self.list_url, {'search': 'Riyadh'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_search_by_description(self):
        """Test searching properties by description"""
        response = self.client.get(self.list_url, {'search': 'Beautiful'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Property Riyadh')

    def test_search_by_city(self):
        """Test searching properties by city in search field"""
        response = self.client.get(self.list_url, {'search': 'Jeddah'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_ordering_by_price(self):
        """Test ordering properties by price"""
        # Ascending order
        response = self.client.get(self.list_url, {'ordering': 'price_per_day'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'Budget Property Riyadh')
        self.assertEqual(results[-1]['name'], 'Luxury Property Dammam')
        
        # Descending order
        response = self.client.get(self.list_url, {'ordering': '-price_per_day'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'Luxury Property Dammam')
        self.assertEqual(results[-1]['name'], 'Budget Property Riyadh')

    def test_ordering_by_created_at(self):
        """Test ordering properties by creation date"""
        response = self.client.get(self.list_url, {'ordering': 'created_at'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        
        response = self.client.get(self.list_url, {'ordering': '-created_at'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_property_detail(self):
        """Test retrieving property details"""
        url = reverse('property-detail', kwargs={'pk': self.property1.pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Property Riyadh')
        self.assertEqual(response.data['city'], 'Riyadh')
        self.assertIn('amenities', response.data)
        self.assertIn('gallery_images', response.data)
        self.assertIn('reviews_avg', response.data)

    def test_property_detail_not_found(self):
        """Test retrieving non-existent property returns 404"""
        url = reverse('property-detail', kwargs={'pk': 9999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_property_gallery(self):
        """Test retrieving property gallery"""
        url = reverse('property-gallery', kwargs={'pk': self.property1.pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['caption'], 'Side view')
        self.assertEqual(response.data[1]['caption'], 'Main view')

    def test_property_gallery_empty(self):
        """Test retrieving gallery for property with no images"""
        url = reverse('property-gallery', kwargs={'pk': self.property2.pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_property_gallery_not_found(self):
        """Test retrieving gallery for non-existent property returns 404"""
        url = reverse('property-gallery', kwargs={'pk': 9999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_pagination_default(self):
        """Test default pagination behavior"""
        response = self.client.get(self.list_url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 4)

    def test_pagination_with_page_size(self):
        """Test pagination with custom page size"""
        response = self.client.get(self.list_url, {'page_size': 2}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['next'])
        
        # Test second page
        response = self.client.get(self.list_url, {'page_size': 2, 'page': 2}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_search_endpoint(self):
        """Test the dedicated search endpoint"""
        url = reverse('property_search')
        response = self.client.get(url, {'search': 'Property'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        
        response = self.client.get(url, {'search': 'Budget'}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class ReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='password')
        self.client.force_authenticate(user=self.user)
        self.owner = User.objects.create_user(username='owner', password='password')
        self.property = Property.objects.create(name='Prop', owner=self.owner, capacity=10)
        self.list_url = reverse('review-list')

    def test_create_review(self):
        data = {
            'property': self.property.id,
            'rating': 5,
            'comment': 'Great!'
        }
        response = self.client.post(self.list_url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PropertyReview.objects.count(), 1)

class BookingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='client', password='password')
        self.client.force_authenticate(user=self.user)
        self.owner = User.objects.create_user(username='owner', password='password')
        self.property = Property.objects.create(
            name='Test Property',
            price_per_day=100,
            capacity=5,
            owner=self.owner
        )
        self.list_url = reverse('booking-list')

    def test_create_booking(self):
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(days=1)
        data = {
            'property': self.property.id,
            'start_datetime': start,
            'end_datetime': end,
            'booking_type': 'full_day',
            'customer_name': 'Client User Name One',
            'customer_phone': '0500000000'
        }
        response = self.client.post(self.list_url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        
    def test_overlap(self):
        start = timezone.now() + timedelta(days=5)
        end = start + timedelta(days=1)
        Booking.objects.create(
            user=self.user,
            property=self.property,
            booking_date=start.date(),
            start_datetime=start,
            end_datetime=end,
            status='confirmed',
            total_price=100,
            customer_name='Overlap User',
            customer_phone='0500000000'
        )
        data = {
            'property': self.property.id,
            'start_datetime': start,
            'end_datetime': end,
            'booking_type': 'full_day',
            'customer_name': 'Client User Name One',
            'customer_phone': '0500000000'
        }
        response = self.client.post(self.list_url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_availability(self):
        start = timezone.now() + timedelta(days=10)
        end = start + timedelta(days=1)
        url = reverse('booking-check-availability')
        data = {
            'property_id': self.property.id,
            'start_datetime': start.isoformat(),
            'end_datetime': end.isoformat()
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['available'])

class PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='client', password='password')
        self.client.force_authenticate(user=self.user)
        self.property = Property.objects.create(name='Prop', capacity=5, price_per_day=100)
        self.booking = Booking.objects.create(
            user=self.user,
            property=self.property,
            booking_date=timezone.now().date(),
            total_price=100,
            customer_name='Payment User',
            customer_phone='0500000000'
        )
        self.provider = PaymentProvider.objects.create(name='Bank', account_number='123')
        
    def test_submit_payment(self):
        url = reverse('payment_submit')
        data = {
            'booking': self.booking.id,
            'payment_method': 'bank_transfer',
            'provider': self.provider.id,
            'transaction_id': 'TX123',
            'payer_full_name': 'Payer Name Test One',
            'amount': 100
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'pending')

