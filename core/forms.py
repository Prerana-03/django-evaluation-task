from django import forms
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile, TaskCompletion, AndroidApp


class SignUpForm(UserCreationForm):
    """Extended user registration form"""
    email = forms.EmailField(max_length=254, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


class TaskCompletionForm(forms.ModelForm):
    """Form for submitting task completion with screenshot"""
    class Meta:
        model = TaskCompletion
        fields = ['screenshot']
        widgets = {
            'screenshot': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control dropzone',
                'id': 'screenshot-upload'
            }),
        }
        
    def clean_screenshot(self):
        """Validate screenshot file"""
        screenshot = self.cleaned_data.get('screenshot')
        
        if not screenshot:
            raise forms.ValidationError("Screenshot is required")
        
        # Check file extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
        validator = FileExtensionValidator(allowed_extensions)
        validator(screenshot)
        
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if screenshot.size > max_size:
            raise forms.ValidationError("File size must be no more than 5MB")
        
        return screenshot


class AndroidAppForm(forms.ModelForm):
    """Form for creating and editing Android apps"""
    class Meta:
        model = AndroidApp
        fields = ['name', 'package_name', 'description', 'points']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'package_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'com.example.app'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
