from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with Arabic labels"""
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'أدخل الاسم الرباعي'
        }),
        label='اسم العميل (رباعي)'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'البريد الإلكتروني'
        }),
        label='البريد الإلكتروني'
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'رقم هاتف العميل'
        }),
        label='رقم هاتف العميل'
    )
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            names = full_name.strip().split()
            if len(names) < 4:
                raise forms.ValidationError('يجب إدخال الاسم الرباعي (أربعة أسماء على الأقل)')
        return full_name

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'اسم المستخدم'
        })
        self.fields['username'].label = 'اسم المستخدم'
        
        self.fields['password1'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'كلمة المرور'
        })
        self.fields['password1'].label = 'كلمة المرور'
        
        self.fields['password2'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'تأكيد كلمة المرور'
        })
        self.fields['password2'].label = 'تأكيد كلمة المرور'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with Arabic labels"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'اسم المستخدم أو البريد الإلكتروني'
        })
        self.fields['username'].label = 'اسم المستخدم'
        
        self.fields['password'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'كلمة المرور'
        })
        self.fields['password'].label = 'كلمة المرور'


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with Arabic labels"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'البريد الإلكتروني'
        })
        self.fields['email'].label = 'البريد الإلكتروني'


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with Arabic labels"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'كلمة المرور الجديدة'
        })
        self.fields['new_password1'].label = 'كلمة المرور الجديدة'
        
        self.fields['new_password2'].widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'تأكيد كلمة المرور الجديدة'
        })
        self.fields['new_password2'].label = 'تأكيد كلمة المرور الجديدة'


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'البريد الإلكتروني'
        }),
        label='البريد الإلكتروني'
    )

    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone_number', 'address', 'date_of_birth', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'أدخل الاسم الرباعي'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'رقم الهاتف'
            }),
            'address': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'placeholder': 'العنوان',
                'rows': 3
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full'
            })
        }
        labels = {
            'full_name': 'اسم العميل (رباعي)',
            'phone_number': 'رقم الهاتف',
            'address': 'العنوان',
            'date_of_birth': 'تاريخ الميلاد',
            'profile_picture': 'صورة الملف الشخصي'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class AccountDeletionForm(forms.Form):
    """Form for account deletion confirmation"""
    confirm_deletion = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox checkbox-error'
        }),
        label='أؤكد رغبتي في حذف حسابي نهائياً'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'كلمة المرور للتأكيد'
        }),
        label='كلمة المرور'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError('كلمة المرور غير صحيحة')
        return password