from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    UserProfileForm, 
    AccountDeletionForm
)
from .models import UserProfile
from booking.models import Booking


class RegisterView(CreateView):
    """User registration view"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'تم إنشاء حسابك بنجاح! يمكنك الآن تسجيل الدخول.')
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('portfolio:home')
        return super().dispatch(request, *args, **kwargs)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('portfolio:home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'مرحباً بك {user.get_full_name() or user.username}!')
                next_url = request.GET.get('next', 'portfolio:home')
                return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'تم تسجيل خروجك بنجاح.')
    return redirect('portfolio:home')


@login_required
def profile_view(request):
    """User profile view"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث ملفك الشخصي بنجاح!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    # Get user bookings
    user_bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
        'bookings': user_bookings
    })


@login_required
def delete_account_view(request):
    """Account deletion view"""
    if request.method == 'POST':
        form = AccountDeletionForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'تم حذف حسابك بنجاح.')
            return redirect('portfolio:home')
    else:
        form = AccountDeletionForm(request.user)
    
    return render(request, 'accounts/delete_account.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        messages.success(self.request, 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view"""
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

    def form_valid(self, form):
        messages.success(self.request, 'تم تغيير كلمة المرور بنجاح! يمكنك الآن تسجيل الدخول.')
        return super().form_valid(form)


def password_reset_done_view(request):
    """Password reset done view"""
    return render(request, 'accounts/password_reset_done.html')


def password_reset_complete_view(request):
    """Password reset complete view"""
    return render(request, 'accounts/password_reset_complete.html')


class CustomPasswordChangeView(PasswordChangeView):
    """Custom password change view"""
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        messages.success(self.request, 'تم تغيير كلمة المرور بنجاح!')
        return super().form_valid(form)
