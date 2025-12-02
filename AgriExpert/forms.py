from django import forms
from .models import Farmer, Expert
from django.core.exceptions import ValidationError
from supabase import create_client, Client
import os
import re
from django.contrib.auth.hashers import make_password
from .models import ExpertPost, ExpertPostImage
from .models import FarmerPost, FarmerPostImage
from .models import Admin

# Load Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ROLE_CHOICES = [
    ('AgriExpert_farmer', 'Magsasaka'),
    ('AgriExpert_expert', 'Eksperto'),
    ('AgriExpert_admin', 'Admin'),
]

class PasswordResetRequestForm(forms.Form):
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Gampanin", widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        email = cleaned_data.get("email")

        if role and email:
            # Query Supabase to check if the email exists in the selected role's table
            response = supabase.table(role).select("id").eq("email", email).execute()

            # If the response contains no data, the email does not exist
            if not response.data:
                self.add_error('email', "Walang rehistradong email para sa napiling gampanin.")

        return cleaned_data
class FarmerSignupForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ["username", "email", "password", "first_name", "middle_name", "last_name", "barangay", "phone_number", "profile_picture", "farm_size"]
        
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) < 4:
            raise forms.ValidationError("Dapat hindi bababa sa 4 na letra ang username.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise forms.ValidationError("Dapat isang wastong email address.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise forms.ValidationError("Dapat mga letra lamang ang unang pangalan.")
        return first_name

    def clean_middle_name(self):
        middle_name = self.cleaned_data.get("middle_name")
        if middle_name and not middle_name.isalpha():
            raise forms.ValidationError("Dapat mga letra lamang ang gitnang pangalan.")
        return middle_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name.isalpha():
            raise forms.ValidationError("Dapat mga letra lamang ang apelyido.")
        return last_name

    def clean_barangay(self):
        barangay = self.cleaned_data.get("barangay")
        if len(barangay) < 3:
            raise forms.ValidationError("Dapat hindi bababa sa 3 letra ang barangay.")
        return barangay

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not re.match(r'^\d+$', phone_number):  # ✅ Ensure only digits
            raise forms.ValidationError("Dapat numero lamang ang phone number.")
        if len(phone_number) < 10 or len(phone_number) > 11:
            raise forms.ValidationError("Dapat 10 o 11 na numero ang phone number.")
        return phone_number

    def clean_farm_size(self):
        farm_size = self.cleaned_data.get("farm_size")
        if farm_size <= 0:
            raise forms.ValidationError("Dapat mas mataas sa 0 ang lawak ng sakahan.")
        return farm_size
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 6:
            raise forms.ValidationError("Dapat hindi bababa sa 6 na letra ang password.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])  # ✅ Hash password before saving
        if commit:
            user.save()
        return user
class ExpertSignupForm(forms.ModelForm):
    class Meta:
        model = Expert
        fields = ["username", "email", "password", "first_name", "middle_name", "last_name", "barangay", "phone_number", "profile_picture", "role", "proof_of_expertise", "license_number", "position"]
        
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) < 4:
            raise forms.ValidationError("Dapat hindi bababa sa 4 na letra ang username.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise forms.ValidationError("Dapat isang wastong email address.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise forms.ValidationError("Dapat mga letra lamang ang unang pangalan.")
        return first_name

    def clean_middle_name(self):
        middle_name = self.cleaned_data.get("middle_name")
        if middle_name and not middle_name.isalpha():
            raise forms.ValidationError("Dapat mga letra lamang ang gitnang pangalan.")
        return middle_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name.isalpha():
            raise forms.ValidationError("Dapat mga letra lamang ang apelyido.")
        return last_name

    def clean_barangay(self):
        barangay = self.cleaned_data.get("barangay")
        if len(barangay) < 3:
            raise forms.ValidationError("Dapat hindi bababa sa 3 letra ang barangay.")
        return barangay

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not re.match(r'^\d+$', phone_number):
            raise forms.ValidationError("Dapat numero lamang ang phone number.")
        if len(phone_number) < 10 or len(phone_number) > 11:
            raise forms.ValidationError("Dapat 10 o 11 na numero ang phone number.")
        return phone_number

    def clean_license_number(self):
        license_number = self.cleaned_data.get("license_number")
        if len(license_number) < 6:
            raise forms.ValidationError("Dapat hindi bababa sa 6 na numero ang license number.")
        return license_number
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 6:
            raise forms.ValidationError("Dapat hindi bababa sa 6 na letra ang password.")
        return password
    def clean_position(self):
        position = self.cleaned_data.get("position")
        if len(position) < 3:
            raise forms.ValidationError("Dapat hindi bababa sa 3 letra ang posisyon.")
        return position
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "Eksperto"
        user.password = make_password(self.cleaned_data["password"])  # ✅ Hash password before saving
        if commit:
            user.save()
        return user
# ROLE_CHOICES = [
#     ('AgriExpert_farmer', 'Magsasaka'),
#     ('AgriExpert_expert', 'Eksperto'),
#     ('AgriExpert_admin', 'Admin'),
# ]

# class PasswordResetRequestForm(forms.Form):
#     role = forms.ChoiceField(choices=ROLE_CHOICES, label="Gampanin")
#     email = forms.EmailField(label="Email Address")

# class PasswordResetConfirmForm(forms.Form):
#     new_password = forms.CharField(widget=forms.PasswordInput, label="Bagong Password")
#     confirm_password = forms.CharField(widget=forms.PasswordInput, label="Kumpirmahin ang Bagong Password")

class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Bagong Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Kumpirmahin ang Bagong Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "Ang password ay hindi magkatugma. Pakisubukan muli.")

        return cleaned_data


class ExpertPostForm(forms.ModelForm):
    class Meta:
        model = ExpertPost
        fields = ['title', 'caption']

class ExpertPostImageForm(forms.ModelForm):
    class Meta:
        model = ExpertPostImage
        fields = ['image_url', 'caption']


class FarmerPostForm(forms.ModelForm):
    class Meta:
        model = FarmerPost
        fields = ['title', 'caption']

class FarmerPostImageForm(forms.ModelForm):
    class Meta:
        model = FarmerPostImage
        fields = ['image_url', 'caption']
        
        
class ExpertProfileUpdateForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kasalukuyang Password'
        }),
        label='Kasalukuyang Password'
    )
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bagong Password (Optional)'
        }),
        label='Bagong Password (Optional)',
        required=False
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kumpirmahin ang Bagong Password'
        }),
        label='Kumpirmahin ang Bagong Password',
        required=False
    )
    
    class Meta:
        model = Expert
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'phone_number', 
                 'barangay', 'license_number', 'position', 'profile_picture']
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unang Pangalan'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gitnang Pangalan (Optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apelyido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'barangay': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Barangay'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'License Number'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Position (Optional)'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        
        labels = {
            'first_name': 'Unang Pangalan',
            'middle_name': 'Gitnang Pangalan',
            'last_name': 'Apelyido',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'barangay': 'Barangay',
            'license_number': 'License Number',
            'position': 'Position',
            'profile_picture': 'Profile Picture'
        }
class AdminProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        }),
        required=False,
        label="Current Password for Verification"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        required=False,
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirm new password'
        }),
        required=False,
        label="Confirm New Password"
    )
    # REMOVE profile_picture field from here - we handle it separately

    class Meta:
        model = Admin
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'organization', 'position']
        # Remove 'profile_picture' from fields
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter middle name (optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter organization name'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your position'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")
        
        return cleaned_data
    
from .models import Announcement
from django.utils import timezone

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'status', 'priority', 'target_audience', 'start_date', 'end_date', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter announcement title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter announcement content'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'target_audience': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }