from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import *
import re

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        
        # Minimum length validation
        if len(new_password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # Check for at least one digit
        if not re.search(r'\d', new_password1):
            raise forms.ValidationError("Password must contain at least one number.")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', new_password1):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', new_password1):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        return new_password1

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Passwords do not match. Please enter the same password in both fields.")
        return new_password2

class UserUpdateProfileForm(forms.ModelForm):
    username_display = forms.CharField(label="Username", required=False, disabled=True)
    email_display = forms.CharField(label="Email", required=False, disabled=True)
    phone_display = forms.CharField(label="Phone", required=False, disabled=True)
    country_display = forms.CharField(label="Country", required=False, disabled=True)
    state_display = forms.CharField(label="State", required=False, disabled=True)
    cities_display = forms.CharField(label="Cities", required=False, disabled=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "name",
            "gender",
            "country",
            "state",
            "cities",
            "profile_picture",
            "card_header",
        ]
        widgets = {
            'cities': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

        # Set the display fields as plain text (disabled)
        if instance:
            self.fields["username_display"].initial = instance.username
            self.fields["email_display"].initial = instance.email
            self.fields["phone_display"].initial = instance.phone
            
            # Set display fields for location
            self.fields["country_display"].initial = instance.country.name if instance.country else ''
            self.fields["state_display"].initial = instance.state.name if instance.state else ''
            self.fields["cities_display"].initial = ', '.join([city.name for city in instance.cities.all()]) if instance.cities.exists() else ''

        # Make fields read-only for role 2
        if self.request and self.request.user.role.id == 2:
            for field in ['country', 'state', 'cities']:
                # Instead of HiddenInput, use disabled fields to preserve values
                self.fields[field].disabled = True
                self.fields[field].required = False
                
                # Set initial values from instance
                if instance:
                    if field == 'country' and instance.country:
                        self.fields[field].initial = instance.country.id
                    elif field == 'state' and instance.state:
                        self.fields[field].initial = instance.state.id
                    elif field == 'cities':
                        self.fields[field].initial = [city.id for city in instance.cities.all()]

    def clean(self):
        cleaned_data = super().clean()
        
        # For role 2, preserve existing location data if form fields are disabled
        if self.request and self.request.user.role.id == 2 and self.instance:
            # Ensure location fields retain their original values
            if self.instance.country:
                cleaned_data['country'] = self.instance.country
            if self.instance.state:
                cleaned_data['state'] = self.instance.state
            if self.instance.cities.exists():
                cleaned_data['cities'] = list(self.instance.cities.all())
                
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # For role 2, explicitly preserve location fields
        if self.request and self.request.user.role.id == 2 and self.instance:
            instance.country = self.instance.country
            instance.state = self.instance.state
            # Cities will be handled in the view since it's M2M
            
        if commit:
            instance.save()
            
        return instance 
