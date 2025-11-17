# ================================
# Django Core and Utility Imports
# ================================
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags
from django.views import View
from django.views.generic import DeleteView
from datetime import datetime
from django.http import HttpResponseForbidden, HttpResponseBadRequest,Http404
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

# =============================
# Django Authentication & Auth
# =============================
from django.contrib import messages
from django.contrib.auth import (
    authenticate, login, logout, get_user_model
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

# ======================
# Django ORM & DB Tools
# ======================
from django.db.models import Q, Sum, F, Prefetch

# =======================
# Third-Party Dependencies
# =======================
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph

# ========================
# Standard Library Modules
# ========================
import os
import json
import csv
import string
import random
import openpyxl
from io import BytesIO, StringIO
from datetime import datetime, date, timedelta
from calendar import month_name

# ================================
# Application-Specific Imports
# ================================
from reward_admin.models import *
from reward_admin.forms import *


# Utility function to generate a unique filename for uploaded images
def generate_unique_filename(prefix, extension):
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{prefix}_{random_str}.{extension}"
  
############################ User Active & Deactivate Function ########################################
class ToggleUserStatusView(View):
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        requested_action = request.POST.get("status") 
        # Determine the source page based on user role
        role_redirect_map = {
            3: "club_member_list",
        }
        source_page = role_redirect_map.get(user.role_id, "view_dashboard")
        # Check if the user is a superuser (role_id == 1)
        if user.role_id == 1:
            messages.error(request, "Superuser status cannot be changed.")
            return redirect("view_dashboard")
        # Prevent self-deactivation
        if user == request.user and requested_action == "deactivate":
            messages.info(
                request, "Your account has been deactivated. Please log in again."
            )
            user.is_active = False
            user.save()
            return redirect(reverse("adminlogin"))
        # Update the user's status based on the requested action
        if requested_action == "activate":
            user.is_active = True
            messages.success(request, f"{user.username} has been activated.")
        elif requested_action == "deactivate":
            user.is_active = False
            messages.success(request, f"{user.username} has been deactivated.")
        else:
            # Fallback: toggle based on current status
            user.is_active = not user.is_active
            status_text = "activated" if user.is_active else "deactivated"
            messages.success(request, f"{user.username} has been {status_text}.")
        user.save()
        return redirect(reverse(source_page))

############################################################################################################################################
# Login Module
def LoginFormView(request):
    # If the user is already logged in, redirect to the dashboard
    if request.user.is_authenticated:
        # Redirect based on user role
        if request.user.role.id in [1]:
            return redirect('view_dashboard')
        
    if request.method == "POST":
        # Get form data directly from request.POST
        login_input = request.POST.get("phone")
        password = request.POST.get("password")
        remember_me = request.POST.get("rememberMe") == "on"

        # Basic validation
        errors = {}
        if not login_input:
            errors['phone'] = 'Phone/Email/Username is required'
        if not password:
            errors['password'] = 'Password is required'

        if not errors:
            user = authenticate_username_email_or_phone(login_input, password)

            if user is not None:
                if user.is_active:
                    if user.role_id in [1, 2]:  # All allowed roles
                        login(request, user)
                        if remember_me:
                            request.session.set_expiry(1209600)
                        messages.success(request, "Login Successful")
                    
                    else:
                        messages.error(
                            request,
                            "You do not have the required role to access this site.",
                        )
                else:
                    messages.error(
                        request,
                        "Your account is deactivated. Please contact the admin.",
                    )
            else:
                messages.error(request, "Invalid login credentials")
        else:
            for error in errors.values():
                messages.error(request, error)

    # Context for template - we'll pass empty values or previously submitted values
    context = {
        'phone_value': request.POST.get('phone', ''),
        'password_value': request.POST.get('password', ''),
        'remember_me_checked': 'checked' if request.POST.get('rememberMe') == 'on' else '',
    }
    
    return render(request, "Admin_Login.html", context)
# Authenticate username, email or phone
def authenticate_username_email_or_phone(login_input, password):
    try:
        if login_input.isdigit():
            user = User.objects.get(phone=login_input)
        elif '@' in login_input:
            user = User.objects.get(email=login_input)
        else:
            # Try username first, then membership_id
            user = User.objects.filter(username=login_input).first() or \
                   User.objects.get(membership_id=login_input)
    except User.DoesNotExist:
        return None
    except User.MultipleObjectsReturned:
        return None
    except Exception as e:
        return None

    if user:
        return authenticate(username=user.username, password=password)
    return None

################################ Dashboard View ##########################################
class Dashboard(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect('adminlogin')
    
                
        total_customer_users = User.objects.filter(role_id=2).count()
        


        # ========================================
        # CONTEXT PREPARATION
        # ========================================
        
        context = {
            'total_customer_users': total_customer_users,
        }
        
        return render(request, "Admin/Dashboard.html", context)



############################################## Logout Module ##################################################
def logout_view(request):
    logout(request)
    return redirect("adminlogin")


################################## Send Welcome Email to Club Member #########################################
def send_welcome_email(email, membership_id, name, password, system_settings, subject, request):
    try:
        logo = system_settings.website_logo if system_settings and system_settings.website_logo else ''
        logo_url = f"{settings.MEDIA_DOMAIN}{logo}" if logo else ''
        static_url = f"{settings.STATIC_DOMAIN}"
        website_name = system_settings.website_name if system_settings else 'Baroda Presidency Club'
        
        # Prepare context for email template
        context = {
            'name': name,
            'membership_id': membership_id,
            'current_year': datetime.now().year,
            'email': email,
            'password': password,
            'logo': logo_url,
            'static_url': static_url,
            'website_name': website_name,
        }
        
        email_content = render_to_string('emails/welcome_email.html', context)
        
        # Send the email
        send_mail(
            subject=subject,
            message=f'Welcome {name} to {website_name}',  # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=email_content,
            fail_silently=False,
        )
        return True
        
    except Exception as e:
        return False


def send_password_change_email(email, membership_id, name, password, system_settings, request):
    try:
        logo = system_settings.website_logo if system_settings and system_settings.website_logo else ''
        logo_url = f"{settings.MEDIA_DOMAIN}{logo}" if logo else ''
        static_url = f"{settings.STATIC_DOMAIN}"
        website_name = system_settings.website_name if system_settings else 'Baroda Presidency Club'
        
        # Prepare context for email template
        context = {
            'name': name,
            'membership_id': membership_id,
            'current_year': datetime.now().year,
            'email': email,
            'password': password,
            'logo': logo_url,
            'static_url': static_url,
            'website_name': website_name,
        }
        
        email_content = render_to_string('emails/password_change_email.html', context)
        
        # Send the email
        send_mail(
            subject='Your Password Has Been Updated',
            message=f'Your password for {website_name} has been updated',  # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=email_content,
            fail_silently=False,
        )
        return True
        
    except Exception as e:
        return False

######################### SystemSettings view #######################################################
class System_Settings(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            system_settings = SystemSettings.objects.create(
                phone="+1234567890"  # Default phone number
            )
        return render(
            request,
            "Admin/System_Settings.html",
            {
                "system_settings": system_settings,
                "MEDIA_URL": settings.MEDIA_URL,
                "breadcrumb": {
                    "parent": "Admin",
                    "child": "System Settings",
                },
            },
        )

    def post(self, request, *args, **kwargs):
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            system_settings = SystemSettings()

        errors = {}

        try:
            # Handle file uploads
            file_fields = {
                "fav_icon": "fav_icon",
                "website_logo": "website_logo",
            }

            for field_name, field_label in file_fields.items():
                if field_name in request.FILES:
                    field_file = request.FILES[field_name]
                    
                    # Validate file type
                    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
                    file_extension = field_file.name.split('.')[-1].lower()
                    
                    if file_extension not in allowed_extensions:
                        errors[field_name] = f"Only {', '.join(allowed_extensions)} files are allowed"
                        continue
                    
                    # Validate file size (max 5MB)
                    if field_file.size > 5 * 1024 * 1024:
                        errors[field_name] = "File size must be less than 5MB"
                        continue
                    
                    current_file = getattr(system_settings, field_label, None)

                    # Remove old file if it exists
                    if current_file:
                        old_file_path = os.path.join(settings.MEDIA_ROOT, str(current_file))
                        if os.path.isfile(old_file_path):
                            try:
                                os.remove(old_file_path)
                            except OSError:
                                pass

                    # Generate a unique filename and store the file
                    file_extension = field_file.name.split(".")[-1]
                    unique_suffix = get_random_string(8)
                    file_filename = f"system_settings/{field_label}_{unique_suffix}.{file_extension}"
                    
                    # Save the file using default storage
                    image_path = default_storage.save(file_filename, field_file)
                    
                    # Update the system_settings with the new file path
                    setattr(system_settings, field_label, image_path)

            # Handle required phone field
            phone = request.POST.get('phone', '').strip()
            if not phone:
                errors['phone'] = "Phone number is required"
            else:
                system_settings.phone = phone

            # Handle optional website_name field
            website_name = request.POST.get('website_name', '').strip()
            system_settings.website_name = website_name if website_name else None

            # Handle optional email field with validation
            email = request.POST.get('email', '').strip()
            if email:
                try:
                    validate_email(email)
                    system_settings.email = email
                except DjangoValidationError:
                    errors['email'] = "Please enter a valid email address"
            else:
                system_settings.email = None

            # Handle optional address field
            address = request.POST.get('address', '').strip()
            system_settings.address = address if address else None
            
            # Save if no errors
            if not errors:
                system_settings.save()
                messages.success(request, "System settings updated successfully.")
                return redirect("System_Settings")
            else:
                messages.error(request, "Please correct the errors below.")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            errors['general'] = str(e)

        # Return form with errors
        return render(
            request,
            "Admin/System_Settings.html",
            {
                "system_settings": system_settings,
                "MEDIA_URL": settings.MEDIA_URL,
                "breadcrumb": {"parent": "Admin", "child": "System Settings"},
                "errors": errors,
            },
        )

##################################################### User Change Password View ###############################################################
def change_password_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            # Log the user out after password change
            logout(request)
            # Add a success message for the user (optional)
            messages.success(request, "Your password has been successfully updated! Please log in with your new credentials.")
            
            # Return the success response with a redirect URL
            return JsonResponse({'success': 'Your password has been successfully updated!',
                                  'redirect': '/adminlogin/'})  # Redirect to login page after password change
        else:
            errors = {}
            for field in form.errors:
                errors[field] = form.errors.get(field)
            return JsonResponse({'errors': errors})

    return JsonResponse({'error': 'Invalid request'}, status=400)

##################################################### User Profile View ###############################################################
class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        context = {
            "user": user,
            "breadcrumb": {"parent": "Acccount", "child": "Profile"},
        }

        return render(request, "Admin/User/User_Profile.html", context)

    def post(self, request):
        user = request.user

        return render(request, "Admin/User/User_Profile.html", {"user": user})


class UserUpdateProfileView(View):
    def get(self, request, *args, **kwargs):
        countries = Country.objects.all()
        cities = City.objects.all()
        user = request.user
        genders = UserGender.objects.all()
        
        return render(
            request,
            "Admin/User/Edit_Profile.html",
            {
                "user": user,
                "countries": countries,
                "cities": cities,
                "genders": genders,
                "errors": {},
                "breadcrumb": {"parent": "Account", "child": "Edit Profile"},
            },
        )

    def post(self, request, *args, **kwargs):
        user = request.user
        errors = {}
        
        # Basic info validation
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        name = request.POST.get('name', '').strip()
        
        # Validate required fields
        if not first_name:
            errors['first_name'] = ['First name is required']
        if not last_name:
            errors['last_name'] = ['Last name is required']
        if not name:
            errors['name'] = ['Full name is required']
        
        # Handle gender properly
        gender_id = request.POST.get('gender', '').strip()
        if gender_id:
            try:
                user.gender = UserGender.objects.get(id=int(gender_id))
            except (UserGender.DoesNotExist, ValueError):
                errors['gender'] = ['Invalid gender selected']
        else:
            user.gender = None
        
        # Update basic info
        user.first_name = first_name
        user.last_name = last_name
        user.name = name
        
        # Location info (only for non-role 2 users)
        if user.role.id != 2:
            country_id = request.POST.get('country')
            state_id = request.POST.get('state')
            city_id = request.POST.get('city')  # Single city now
            
            if country_id:
                try:
                    country = Country.objects.get(id=country_id)
                    user.country = country
                except (Country.DoesNotExist, ValueError):
                    errors['country'] = ['Invalid country selected']
            else:
                user.country = None
            
            if state_id:
                try:
                    state = State.objects.get(id=state_id)
                    # Validate that state belongs to selected country
                    if user.country and state.country != user.country:
                        errors['state'] = ['State does not belong to selected country']
                    else:
                        user.state = state
                except (State.DoesNotExist, ValueError):
                    errors['state'] = ['Invalid state selected']
            else:
                user.state = None
            
            # Single city selection
            if city_id:
                try:
                    city = City.objects.get(id=city_id)
                    # Validate that city belongs to selected state
                    if user.state and city.state != user.state:
                        errors['city'] = ['City does not belong to selected state']
                    else:
                        # Clear existing cities and add the selected one
                        user.cities.clear()
                        user.cities.add(city)
                except (City.DoesNotExist, ValueError):
                    errors['city'] = ['Invalid city selected']
            else:
                user.cities.clear()
        
        # Additional fields from model
        date_of_birth = request.POST.get('date_of_birth', '').strip()
        if date_of_birth:
            try:
                user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                errors['date_of_birth'] = ['Invalid date format. Use YYYY-MM-DD']
        else:
            user.date_of_birth = None
        
        user.address = request.POST.get('address', '').strip() or None
        user.pincode = request.POST.get('pincode', '').strip() or None
        
        # Handle file uploads
        fs_profile = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "profile_pics"))
        fs_card = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "card_header"))

        # Handle profile picture
        if "profile_picture" in request.FILES:
            profile_pic = request.FILES["profile_picture"]
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if profile_pic.content_type not in allowed_types:
                errors['profile_picture'] = ['Invalid file type. Only JPEG, PNG, and GIF are allowed.']
            elif profile_pic.size > 5 * 1024 * 1024:  # 5MB limit
                errors['profile_picture'] = ['File too large. Maximum size is 5MB.']
            else:
                # Remove old profile picture
                if user.profile_picture:
                    old_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_picture))
                    if os.path.isfile(old_path):
                        os.remove(old_path)

                ext = profile_pic.name.split(".")[-1]
                filename = f"profile_{user.id}.{ext}"
                fs_profile.save(filename, profile_pic)
                user.profile_picture = os.path.join("profile_pics", filename)

        elif "profile_picture-clear" in request.POST and user.profile_picture:
            old_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_picture))
            if os.path.isfile(old_path):
                os.remove(old_path)
            user.profile_picture = None

        # Handle card header
        if "card_header" in request.FILES:
            card_header = request.FILES["card_header"]
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if card_header.content_type not in allowed_types:
                errors['card_header'] = ['Invalid file type. Only JPEG, PNG, and GIF are allowed.']
            elif card_header.size > 5 * 1024 * 1024:  # 5MB limit
                errors['card_header'] = ['File too large. Maximum size is 5MB.']
            else:
                # Remove old card header
                if user.card_header:
                    old_path = os.path.join(settings.MEDIA_ROOT, str(user.card_header))
                    if os.path.isfile(old_path):
                        os.remove(old_path)

                ext = card_header.name.split(".")[-1]
                filename = f"card_{user.id}.{ext}"
                fs_card.save(filename, card_header)
                user.card_header = os.path.join("card_header", filename)

        elif "card_header-clear" in request.POST and user.card_header:
            old_path = os.path.join(settings.MEDIA_ROOT, str(user.card_header))
            if os.path.isfile(old_path):
                os.remove(old_path)
            user.card_header = None

        # Save the user if no errors
        if not errors:
            try:
                user.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, "Your profile has been updated successfully.")
                return redirect("edit_profile")
            except Exception as e:
                errors['general'] = [f'Error saving profile: {str(e)}']
        
        # Handle errors
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        
        countries = Country.objects.all()
        cities = City.objects.all()
        return render(
            request,
            "Admin/User/Edit_Profile.html",
            {
                "user": user,
                "countries": countries,
                "cities": cities,
                "errors": errors,
                "breadcrumb": {"parent": "Account", "child": "Edit Profile"},
            },
        )

# Improved API endpoints with error handling
def api_get_states(request):
    country_id = request.GET.get('country_id')
    if not country_id:
        return JsonResponse({'error': 'Country ID is required'}, status=400)
    
    try:
        states = State.objects.filter(country_id=country_id).values('id', 'name').order_by('name')
        return JsonResponse(list(states), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_get_cities(request):
    state_id = request.GET.get('state_id')
    if not state_id:
        return JsonResponse({'error': 'State ID is required'}, status=400)
    
    try:
        cities = City.objects.filter(state_id=state_id).values('id', 'name').order_by('name')
        return JsonResponse(list(cities), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
         
################################################################# Role CRUD Views ###################################################

# User Role List Module  
class RoleView(LoginRequiredMixin, View):
    template_name = "Admin/Permissions/User_Role.html"

    def get(self, request):
        roles = Role.objects.all()
        return render(
            request,
            self.template_name,
            {
                "roles": roles,
                "breadcrumb": {"child": "Role List"},
            },
        )

# # Role Create Views
# class RoleCreateView(LoginRequiredMixin, View):
#     def post(self, request):
#         name = request.POST.get("name")

#         if not name:
#             messages.error(request, "Name is required.")
#             return redirect("role_list")

#         try:
#             Role.objects.create(
#                 name=name,
#             )
#             messages.success(request, "Role added successfully.")
#         except Exception as e:
#             messages.error(request, f"Error creating role: {str(e)}")
        
#         return redirect("role_list")

# Role Edit Views
class RoleEditView(LoginRequiredMixin, View):
    def post(self, request, role_id):
        role = get_object_or_404(Role, id=role_id)
        role.name = request.POST.get("name")

        try:
            role.save()
            messages.success(request, "Role updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating role: {str(e)}")
        
        return redirect("role_list")

# Role Delete Views
# class RoleDeleteView(LoginRequiredMixin, View):
#     def post(self, request, role_id):
#         role = get_object_or_404(Role, id=role_id)
#         try:
#             role.delete()
#             messages.success(request, "Role deleted successfully.")
#         except Exception as e:
#             messages.error(request, f"Error deleting role: {str(e)}")
#         return redirect("role_list")

#################################################### Country List View API ##################################################
class CountryListView(View):
    def get(self, request):
        countries = Country.objects.all().order_by('-created_at')
        return render(request, 'Admin/Location/Country_List.html', {
            'countries': countries,
            'breadcrumb': {'child': 'Country Management'}
        })

class CountryCreateView(View):
    def post(self, request):
        code = request.POST.get('code')
        name = request.POST.get('name')
        country_code = request.POST.get('country_code')
        zone_id = request.POST.get('zone_id', 0)
        flag_file = request.FILES.get('flag')
        status = 'status' in request.POST  # Checkbox

        # Validation
        if not code or not name:
            messages.error(request, "Code and Name are required")
            return redirect('country_list')

        if len(code) != 2:
            messages.error(request, "Country code must be exactly 2 characters")
            return redirect('country_list')

        if Country.objects.filter(code=code).exists():
            messages.error(request, "Country code already exists")
            return redirect('country_list')

        try:
            flag_path = None
            if flag_file:
                ext = os.path.splitext(flag_file.name)[1].lstrip(".")  # remove dot
                unique_filename = generate_unique_filename("flag", ext)
                file_path = os.path.join("flags", unique_filename)
                default_storage.save(file_path, flag_file)
                flag_path = file_path  # Save relative path

            country = Country.objects.create(
                code=code.upper(),
                name=name,
                country_code=country_code if country_code else None,
                zone_id=int(zone_id) if zone_id else 0,
                flag=flag_path,
                status=status
            )
            messages.success(request, "Country created successfully")

        except Exception as e:
            messages.error(request, f"Error creating country: {str(e)}")

        return redirect('country_list')

class CountryEditView(View):
    def get(self, request, pk):
        country = get_object_or_404(Country, pk=pk)
        return JsonResponse({
            'id': country.id,
            'code': country.code,
            'name': country.name,
            'country_code': country.country_code,
            'zone_id': country.zone_id,
            'status': country.status,
            'flag_url': country.flag.url if country.flag else None
        })
    
    def post(self, request, pk):
        country = get_object_or_404(Country, pk=pk)
        
        code = request.POST.get('code')
        name = request.POST.get('name')
        country_code = request.POST.get('country_code')
        zone_id = request.POST.get('zone_id', 0)
        flag = request.FILES.get('flag')
        status = 'status' in request.POST
        
        # Validation
        if not code or not name:
            messages.error(request, "Code and Name are required")
            return redirect('country_list')
        
        if len(code) != 2:
            messages.error(request, "Country code must be exactly 2 characters")
            return redirect('country_list')
            
        # Check if country code already exists (excluding current country)
        if Country.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, "Country code already exists")
            return redirect('country_list')
        
        try:
            country.code = code.upper()
            country.name = name
            country.country_code = country_code if country_code else None
            country.zone_id = int(zone_id) if zone_id else 0
            country.status = status
            
            # Handle flag upload
            if flag:
                # Delete old flag if exists
                if country.flag:
                    old_flag_path = country.flag.path
                    if os.path.exists(old_flag_path):
                        os.remove(old_flag_path)

                # Generate new unique filename
                file_extension = os.path.splitext(flag.name)[1].lstrip(".")  # Remove leading dot
                unique_filename = generate_unique_filename("flag", file_extension)
                file_path = os.path.join("flags", unique_filename)

                # Save new file to storage and update model field
                default_storage.save(file_path, flag)
                country.flag.name = file_path

            country.save()
            messages.success(request, "Country updated successfully")
        except Exception as e:
            messages.error(request, f"Error updating country: {str(e)}")
        
        return redirect('country_list')

class CountryDeleteView(View):
    def post(self, request, pk):
        country = get_object_or_404(Country, pk=pk)
        try:
            # Delete flag file if exists
            if country.flag:
                flag_path = country.flag.path
                if os.path.exists(flag_path):
                    os.remove(flag_path)
            
            country.delete()
            messages.success(request, "Country deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting country: {str(e)}")
        
        return redirect('country_list')


#################################  State CRUD #######################################
class StateListView(View):
    def get(self, request):
        states = State.objects.select_related('country').all()
        countries = Country.objects.all()
        return render(request, 'Admin/Location/State_List.html', {
            'states': states,
            'countries': countries,
            'breadcrumb': {'child': 'State Management'}
        })

class StateCreateView(View):
    def post(self, request):
        name = request.POST.get('name')
        country_id = request.POST.get('country')
        status = request.POST.get('status') == 'on'  # Check if checkbox was checked
        
        if not name or not country_id:
            messages.error(request, "Name and Country are required")
            return redirect('state_list')
            
        try:
            State.objects.create(
                name=name,
                country_id=country_id,
                status=status
            )
            messages.success(request, "State created successfully")
        except Exception as e:
            messages.error(request, f"Error creating state: {str(e)}")
        
        return redirect('state_list')

class StateEditView(View):
    def get(self, request, pk):
        state = get_object_or_404(State, pk=pk)
        return JsonResponse({
            'id': state.id,
            'name': state.name,
            'country_id': state.country_id,
            'status': state.status
        })
    
    def post(self, request, pk):
        state = get_object_or_404(State, pk=pk)
        state.name = request.POST.get('name')
        state.country_id = request.POST.get('country')
        state.status = request.POST.get('status') == 'on'  # Check if checkbox was checked
        
        try:
            state.save()
            messages.success(request, "State updated successfully")
        except Exception as e:
            messages.error(request, f"Error updating state: {str(e)}")
        
        return redirect('state_list')

class StateDeleteView(View):
    def post(self, request, pk):
        state = get_object_or_404(State, pk=pk)
        try:
            state.delete()
            messages.success(request, "State deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting state: {str(e)}")
        
        return redirect('state_list')

############################## City List View #################################
class CityListView(LoginRequiredMixin, View):
    template_name = "Admin/Location/City_List.html"

    def get(self, request):
        states = State.objects.all()
        return render(
            request,
            self.template_name,
            {
                "breadcrumb": {"child": "City Management"},
                "states": states,
            },
        )

    def post(self, request):
        # Get DataTables parameters
        draw = int(request.POST.get('draw', 1))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        
        # Get ordering parameters
        order_column_index = int(request.POST.get('order[0][column]', 1))  # Default to name column
        order_direction = request.POST.get('order[0][dir]', 'asc')
        
        # Map DataTables column index to model field
        column_map = {
            0: 'counter',  # Not a real field, handled in processing
            1: 'name',
            2: 'state__name',
            3: 'state__country__name',
            4: 'status',
            5: 'created_at',
            6: 'actions'  # Not sortable
        }
        
        order_column = column_map.get(order_column_index, 'name')
        
        # Set ordering
        if order_direction == 'desc':
            order_column = '-' + order_column
        
        # Base queryset
        queryset = City.objects.select_related('state', 'state__country').all()
        
        # Apply search filter if provided
        if search_value:
            queryset = queryset.filter(
                Q(name__icontains=search_value) |
                Q(state__name__icontains=search_value) |
                Q(state__country__name__icontains=search_value)
            )

        # Apply ordering if not ordering by counter or actions
        if order_column_index != 0 and order_column_index != 6:
            queryset = queryset.order_by(order_column)
        else:
            # Default ordering
            queryset = queryset.order_by('name')

        # Get total records count (before filtering)
        total_records = City.objects.count()
        
        # Get filtered count
        filtered_records = queryset.count()
        
        # Apply pagination
        cities = queryset[start:start + length]
        
        # Prepare data for response
        data = []
        for index, city in enumerate(cities):
            # Check permissions
            can_edit = request.user.has_permission('city_list')
            can_delete = request.user.has_permission('city_list')
            
            # Build actions HTML based on permissions
            actions_html = """
            <div class="action-menu-container" style="position: relative; display: inline-block;">
                <a href="#" class="three-dots-menu">
                    <i data-feather="more-vertical"></i>
                </a>
                <div class="action-card" style="display: none; position: absolute; top: 100%; right: 0; background: #fff; border: 1px solid #ccc; border-radius: 4px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); z-index: 10; width: auto;">
                    <ul style="list-style: none; padding: 0; margin: 0;">
            """
            
            # Edit action
            if can_edit:
                status_str = 'true' if city.status else 'false'
                actions_html += f"""
                        <li style="padding: 8px 12px;">
                            <a style="font-size: small" href="#" 
                                data-bs-toggle="modal" 
                                data-bs-target="#editCityModal"
                                data-city-id="{city.id}"
                                data-city-name="{city.name}"
                                data-state-id="{city.state.id if city.state else ''}"
                                data-city-status="{status_str}"
                                class="text-decoration-none">
                                Edit
                            </a>
                        </li>
                """
            
            # Delete action
            if can_delete:
                actions_html += f"""
                        <li style="padding: 8px 12px; border-top: 1px solid #eee;">
                            <a style="font-size: small;" href="#" 
                                data-bs-toggle="modal" 
                                data-bs-target="#deleteCityModal" 
                                data-city-id="{city.id}"
                                class="text-decoration-none">
                                Delete
                            </a>
                        </li>
                """
            
            actions_html += """
                    </ul>
                </div>
            </div>
            """
            
            # Status badge
            status_badge = f"""
            <span class="badge badge-{'success' if city.status else 'danger'}">
                {'Active' if city.status else 'Inactive'}
            </span>
            """
            
            data.append({
                'counter': start + index + 1,
                'name': city.name,
                'state': city.state.name if city.state else 'N/A',
                'country': city.state.country.name if city.state and city.state.country else 'N/A',
                'status': status_badge,
                'created_at': city.created_at.strftime('%Y-%m-%d %H:%M') if city.created_at else 'N/A',
                'actions': actions_html
            })
        
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data,
        }
        
        return JsonResponse(response)

class CityCreateView(View):
    def post(self, request):
        name = request.POST.get('name')
        state_id = request.POST.get('state')
        status = request.POST.get('status') == 'on'  # Check if checkbox was checked
        
        if not name or not state_id:
            messages.error(request, "Name and State are required")
            return redirect('city_list')
            
        try:
            City.objects.create(
                name=name,
                state_id=state_id,
                status=status
            )
            messages.success(request, "City created successfully")
        except Exception as e:
            messages.error(request, f"Error creating city: {str(e)}")
        
        return redirect('city_list')

class CityEditView(View):
    def get(self, request, pk):
        city = get_object_or_404(City, pk=pk)
        return JsonResponse({
            'id': city.id,
            'name': city.name,
            'state_id': city.state_id,
            'status': city.status
        })
    
    def post(self, request, pk):
        city = get_object_or_404(City, pk=pk)
        city.name = request.POST.get('name')
        city.state_id = request.POST.get('state')
        city.status = request.POST.get('status') == 'on'  # Check if checkbox was checked
        
        try:
            city.save()
            messages.success(request, "City updated successfully")
        except Exception as e:
            messages.error(request, f"Error updating city: {str(e)}")
        
        return redirect('city_list')

class CityDeleteView(View):
    def post(self, request, pk):
        city = get_object_or_404(City, pk=pk)
        try:
            city.delete()
            messages.success(request, "City deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting city: {str(e)}")
        
        return redirect('city_list')

############### Send email to sub-admin with details ###########################
def send_sub_admin_detail(email, name,username,password,subject):
    system_settings = SystemSettings.objects.first()
    logo = system_settings.website_logo if system_settings and system_settings.website_logo else ''
    context = {
        'name': name,
        'username': username,
        'password': password,
        'logo': logo,
    }
    # Render HTML template
    html_content = render_to_string('Admin/Emails/Sub_Admin_Create.html', context)
    
    # Create plain text version (optional but recommended)
    text_content = strip_tags(html_content)
    
    # Create email
    email_msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    email_msg.attach_alternative(html_content, "text/html")
    
    try:
        email_msg.send()
        return True
    except Exception as e:
        return False

########################## Sub Admin Views ###############################
def get_states(request):
    """API endpoint to get all states for country_id=1"""
    try:
        states = State.objects.filter(country_id=1).values('id', 'name').order_by('name')
        return JsonResponse(list(states), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_cities(request):
    """API endpoint to get cities for a specific state"""
    state_id = request.GET.get('state_id')
    if not state_id:
        return JsonResponse([], safe=False)
    
    try:
        cities = City.objects.filter(state_id=state_id).values('id', 'name').order_by('name')
        return JsonResponse(list(cities), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

########################## Customer Views ###############################

class CustomerUserListView(LoginRequiredMixin, View):
    template_name = "Admin/User/Customer_List.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "breadcrumb": {"child": "Customer List"},
            },
        )

    def post(self, request):
        # Get DataTables parameters
        draw = int(request.POST.get('draw', 1))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        
        # Get sorting parameters
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_direction = request.POST.get('order[0][dir]', 'asc')
        
        # Map column index to model field
        column_map = {
            0: 'id',
            1: 'username',
            2: 'first_name',
            3: 'last_name',
            4: 'email',
            5: 'phone',
            6: 'created_at',
        }
        
        # Get the custom user model
        User = get_user_model()
        
        # Base queryset - all customer users (assuming role_id=3 for customers)
        queryset = User.objects.filter(role_id=3)
        
        # Apply sorting if the column is sortable
        if order_column_index in column_map:
            order_field = column_map[order_column_index]
            if order_direction == 'desc':
                order_field = '-' + order_field
            queryset = queryset.order_by(order_field)
        else:
            # Default ordering
            queryset = queryset.order_by('-created_at')
        
        # Apply search filter if provided
        if search_value:
            queryset = queryset.filter(
                Q(username__icontains=search_value) |
                Q(first_name__icontains=search_value) |
                Q(last_name__icontains=search_value) |
                Q(name__icontains=search_value) |
                Q(email__icontains=search_value) |
                Q(phone__icontains=search_value)
            )

        # If current user is not admin (role_id=1), filter by cities
        if request.user.role.id != 1:
            user_cities = request.user.cities.all()
            if user_cities:
                queryset = queryset.filter(cities__in=user_cities).distinct()
            else:
                queryset = User.objects.none()

        # Get total records count (without filters)
        total_records = User.objects.filter(role_id=3).count()
        
        # Get filtered count (with search filters applied)
        filtered_records = queryset.count()
        
        # Apply pagination
        customers = queryset[start:start + length]
        
        # Prepare data for response
        data = []
        for index, customer in enumerate(customers):
            status_badge = 'badge-success' if customer.is_active else 'badge-danger'
            status_text = 'Active' if customer.is_active else 'Inactive'
            
            # Get assigned cities
            cities = ", ".join([city.name for city in customer.cities.all()[:2]])
            if customer.cities.count() > 2:
                cities += f" (+{customer.cities.count() - 2} more)"
            
            # Get full name
            full_name = f"{customer.first_name or ''} {customer.last_name or ''}".strip() or customer.name or 'N/A'
            
            # Check permissions
            can_toggle_status = request.user.has_permission('customer_edit')
            
            # Build actions HTML based on permissions
            actions_html = """
            <div class="action-menu-container" style="position: relative; display: inline-block;">
                <a href="#" class="three-dots-menu">
                    <i class="fa fa-ellipsis-v"></i>
                </a>
                <div class="action-card" style="display: none; position: absolute; top: 100%; right: 0; background: #fff; border: 1px solid #ccc; border-radius: 4px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); z-index: 10; width: auto;">
                    <ul style="list-style: none; padding: 0; margin: 0;">
            """
            
            # Toggle status action
            if can_toggle_status:
                actions_html += f"""
                        <li style="padding: 8px 12px; border-bottom: 1px solid #eee; font-size: small;">
                            <a href="#" class="toggle-status text-decoration-none" data-id="{customer.id}" data-status="{'deactivate' if customer.is_active else 'activate'}">
                                {'Deactivate' if customer.is_active else 'Activate'}
                            </a>
                        </li>
                """
            
            # View action
            actions_html += f"""
                        <li style="padding: 8px 12px; font-size: small;">
                            <a href="/customer/detail/{customer.id}/" class="text-decoration-none">
                                View
                            </a>
                        </li>
            """
            
            actions_html += """
                    </ul>
                </div>
            </div>
            """
            
            data.append({
                'counter': start + index + 1,
                'username': customer.username or 'N/A',
                'first_name': customer.first_name or 'N/A',
                'last_name': customer.last_name or 'N/A',
                'full_name': full_name,
                'email': customer.email or 'N/A',
                'phone': customer.phone or 'N/A',
                'cities': cities or 'N/A',
                'status': f'<span class="badge {status_badge}">{status_text}</span>',
                'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M') if customer.created_at else 'N/A',
                'actions': actions_html
            })
        
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data,
        }
        
        return JsonResponse(response)


######################################## Customer Detail Page #################################################        
class CustomerDetailView(LoginRequiredMixin, View):
    template_name = "Admin/User/Customer_Detail.html"

    def get(self, request, pk):
        try:
            User = get_user_model()
            customer = User.objects.get(id=pk, role_id=3)  # Ensure it's a customer
            
            return render(
                request,
                self.template_name,
                {
                    "customer": customer,
                    "title": "Customer Details",
                },
            )
        except User.DoesNotExist:
            messages.error(request, 'Customer not found')
            return redirect("customer_user_list")

    def post(self, request, pk):
        return self.get(request, pk)


############################## Customer Toggle Status View ###################################
class CustomerToggleStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        User = get_user_model()
        customer = get_object_or_404(User, pk=pk, role_id=3)
        
        # Check permission
        if not request.user.has_permission('customer_edit'):
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to perform this action'
            }, status=403)
        
        try:
            customer.is_active = not customer.is_active
            customer.save()
            
            status = "activated" if customer.is_active else "deactivated"
            messages.success(request, f'Customer {status} successfully')
            return JsonResponse({
                'success': True,
                'message': f'Customer {status} successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error toggling status: {str(e)}'
            }, status=500)
        

######################################### FAQ CRUD #########################################
class FAQView(LoginRequiredMixin, View):
    template_name = "Admin/General_Settings/Faq.html"

    def get(self, request):
        faqs = FAQ.objects.all().order_by('question')
        return render(
            request,
            self.template_name,
            {
                "faqs": faqs,
                "breadcrumb": {"child": "FAQ List"},
            },
        )

# FAQ Create Views
class FAQCreateView(LoginRequiredMixin, View):
    def post(self, request):
        question = request.POST.get("question")
        answer = request.POST.get("answer")

        if not question or not answer:
            messages.error(request, "Both question and answer are required.")
            return redirect("faq_list")

        FAQ.objects.create(
            question=question,
            answer=answer,
        )

        messages.success(request, "FAQ added successfully.")
        return redirect("faq_list")

# FAQ Edit Views 
class FAQEditView(LoginRequiredMixin, View):
    template_name = "Admin/MobileApp/Faq.html"

    def get(self, request, faq_id):
        faq = get_object_or_404(FAQ, id=faq_id)
        return render(request, self.template_name, {"faq": faq})

    def post(self, request, faq_id):
        faq = get_object_or_404(FAQ, id=faq_id)

        question = request.POST.get("question")
        answer = request.POST.get("answer")

        faq.question = question
        faq.answer = answer
        faq.save()

        messages.success(request, "FAQ updated successfully.")
        return redirect("faq_list")

# FAQ Delete Views 
class FAQDeleteView(LoginRequiredMixin, View):
    def post(self, request, faq_id):
        faq = get_object_or_404(FAQ, id=faq_id)
        faq.delete()
        messages.success(request, "FAQ deleted successfully.")
        return redirect("faq_list")


################### Product Category CRUD #########################################
class ProductCategoryListView(View):
    def get(self, request):
        categories = product_category.objects.all().order_by('-created_at')
        return render(request, 'Admin/Product/Category_List.html', {
            'categories': categories,
            'breadcrumb': {'child': 'Product Category Management'}
        })

class ProductCategoryCreateView(View):
    def post(self, request):
        name = request.POST.get('name')
        status = 'status' in request.POST  # Checkbox

        # Validation
        if not name:
            messages.error(request, "Category name is required")
            return redirect('product_category_list')

        if product_category.objects.filter(name=name).exists():
            messages.error(request, "Category name already exists")
            return redirect('product_category_list')

        try:
            category = product_category.objects.create(
                name=name,
                status=status
            )
            messages.success(request, "Product category created successfully")

        except Exception as e:
            messages.error(request, f"Error creating category: {str(e)}")

        return redirect('product_category_list')

class ProductCategoryEditView(View):
    def get(self, request, pk):
        category = get_object_or_404(product_category, pk=pk)
        return JsonResponse({
            'id': category.id,
            'name': category.name,
            'status': category.status,
            'created_at': category.created_at.strftime('%Y-%m-%d %H:%M') if category.created_at else None,
            'updated_at': category.updated_at.strftime('%Y-%m-%d %H:%M') if category.updated_at else None
        })
    
    def post(self, request, pk):
        category = get_object_or_404(product_category, pk=pk)
        
        name = request.POST.get('name')
        status = 'status' in request.POST
        
        # Validation
        if not name:
            messages.error(request, "Category name is required")
            return redirect('product_category_list')
            
        # Check if category name already exists (excluding current category)
        if product_category.objects.filter(name=name).exclude(pk=pk).exists():
            messages.error(request, "Category name already exists")
            return redirect('product_category_list')
        
        try:
            category.name = name
            category.status = status
            category.save()
            messages.success(request, "Product category updated successfully")
        except Exception as e:
            messages.error(request, f"Error updating category: {str(e)}")
        
        return redirect('product_category_list')

class ProductCategoryDeleteView(View):
    def post(self, request, pk):
        category = get_object_or_404(product_category, pk=pk)
        try:
            category.delete()
            messages.success(request, "Product category deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting category: {str(e)}")
        
        return redirect('product_category_list')




class ProductListView(View):
    def get(self, request):
        products = product.objects.all().select_related('category').prefetch_related('images').order_by('-created_at')
        categories = product_category.objects.filter(status=True)
        return render(request, 'Admin/Product/Product_List.html', {
            'products': products,
            'categories': categories,
            'breadcrumb': {'child': 'Product Management'}
        })

class ProductCreateView(View):
    def post(self, request):
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        MRP = request.POST.get('MRP')
        sale_price = request.POST.get('sale_price')
        url = request.POST.get('url')
        status = 'status' in request.POST
        image_files = request.FILES.getlist('images')

        # Validation
        if not name:
            messages.error(request, "Product name is required")
            return redirect('product_list')

        if not category_id:
            messages.error(request, "Category is required")
            return redirect('product_list')

        try:
            with transaction.atomic():
                # Create product
                product_obj = product.objects.create(
                    name=name,
                    category_id=category_id,
                    description=description,
                    MRP=MRP if MRP else None,
                    sale_price=sale_price if sale_price else None,
                    url=url,
                    status=status
                )

                # Handle multiple image uploads
                for image_file in image_files:
                    if image_file:
                        # Validate file type
                        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                        if image_file.content_type not in allowed_types:
                            continue  # Skip invalid files
                        
                        if image_file.size > 5 * 1024 * 1024:  # 5MB limit
                            continue  # Skip files that are too large

                        # Generate unique filename
                        ext = os.path.splitext(image_file.name)[1]
                        unique_filename = generate_unique_filename(f"product_{product_obj.id}", ext.lstrip("."))
                        file_path = os.path.join("product_images", unique_filename)
                        
                        # Save file
                        default_storage.save(file_path, image_file)
                        
                        # Create product image record
                        product_image.objects.create(
                            product=product_obj,
                            image=file_path
                        )

                messages.success(request, "Product created successfully")

        except Exception as e:
            messages.error(request, f"Error creating product: {str(e)}")

        return redirect('product_list')

class ProductEditView(View):
    def get(self, request, pk):
        product_obj = get_object_or_404(product, pk=pk)
        images = product_obj.images.all()
        
        return JsonResponse({
            'id': product_obj.id,
            'name': product_obj.name,
            'category_id': product_obj.category.id,
            'description': product_obj.description,
            'MRP': str(product_obj.MRP) if product_obj.MRP else '',
            'sale_price': str(product_obj.sale_price) if product_obj.sale_price else '',
            'url': product_obj.url,
            'status': product_obj.status,
            'images': [
                {
                    'id': img.id,
                    'url': img.image.url if img.image else None,
                    'name': os.path.basename(img.image.name) if img.image else None
                } for img in images
            ]
        })
    
    def post(self, request, pk):
        product_obj = get_object_or_404(product, pk=pk)
        
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        MRP = request.POST.get('MRP')
        sale_price = request.POST.get('sale_price')
        url = request.POST.get('url')
        status = 'status' in request.POST
        new_images = request.FILES.getlist('new_images')
        delete_images = request.POST.getlist('delete_images')

        # Validation
        if not name:
            messages.error(request, "Product name is required")
            return redirect('product_list')

        if not category_id:
            messages.error(request, "Category is required")
            return redirect('product_list')

        try:
            with transaction.atomic():
                # Update product
                product_obj.name = name
                product_obj.category_id = category_id
                product_obj.description = description
                product_obj.MRP = MRP if MRP else None
                product_obj.sale_price = sale_price if sale_price else None
                product_obj.url = url
                product_obj.status = status
                product_obj.save()

                # Delete selected images
                for image_id in delete_images:
                    try:
                        img = product_image.objects.get(id=image_id, product=product_obj)
                        if img.image:
                            if default_storage.exists(img.image.name):
                                default_storage.delete(img.image.name)
                        img.delete()
                    except product_image.DoesNotExist:
                        continue

                # Add new images
                for image_file in new_images:
                    if image_file:
                        # Validate file type
                        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                        if image_file.content_type not in allowed_types:
                            continue
                        
                        if image_file.size > 5 * 1024 * 1024:  # 5MB limit
                            continue

                        # Generate unique filename
                        ext = os.path.splitext(image_file.name)[1]
                        
                        unique_filename = generate_unique_filename(f"product_{product_obj.id}", ext.lstrip("."))
                        file_path = os.path.join("product_images", unique_filename)
                        
                        # Save file
                        default_storage.save(file_path, image_file)
                        
                        # Create product image record
                        product_image.objects.create(
                            product=product_obj,
                            image=file_path
                        )

                messages.success(request, "Product updated successfully")
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
        
        return redirect('product_list')

class ProductDeleteView(View):
    def post(self, request, pk):
        product_obj = get_object_or_404(product, pk=pk)
        try:
            # Delete all associated images
            images = product_obj.images.all()
            for img in images:
                if img.image:
                    if default_storage.exists(img.image.name):
                        default_storage.delete(img.image.name)
                img.delete()
            
            product_obj.delete()
            messages.success(request, "Product deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting product: {str(e)}")
        
        return redirect('product_list')

class CustomerReviewListView(View):
    def get(self, request):
        reviews = customer_review.objects.all().select_related('product', 'customer').order_by('-created_at')
        return render(request, 'Admin/Review/Review_List.html', {
            'reviews': reviews,
            'breadcrumb': {'child': 'Customer Reviews Management'}
        })

class CustomerReviewDetailView(View):
    def get(self, request, pk):
        review = get_object_or_404(customer_review, pk=pk)
        return JsonResponse({
            'id': review.id,
            'product_name': review.product.name,
            'customer_name': review.customer.name or review.customer.username,
            'customer_email': review.customer.email,
            'rating': review.rating,
            'review': review.review,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M') if review.created_at else None,
            'updated_at': review.updated_at.strftime('%Y-%m-%d %H:%M') if review.updated_at else None
        })

class CustomerReviewEditView(View):
    def get(self, request, pk):
        review = get_object_or_404(customer_review, pk=pk)
        return JsonResponse({
            'id': review.id,
            'rating': review.rating,
            'review': review.review
        })
    
    def post(self, request, pk):
        review = get_object_or_404(customer_review, pk=pk)
        
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')
        
        # Validation
        if not rating:
            messages.error(request, "Rating is required")
            return redirect('customer_review_list')
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, "Rating must be between 1 and 5")
                return redirect('customer_review_list')
        except ValueError:
            messages.error(request, "Rating must be a valid number")
            return redirect('customer_review_list')
        
        try:
            review.rating = rating
            review.review = review_text
            review.save()
            messages.success(request, "Review updated successfully")
        except Exception as e:
            messages.error(request, f"Error updating review: {str(e)}")
        
        return redirect('customer_review_list')

class CustomerReviewDeleteView(View):
    def post(self, request, pk):
        review = get_object_or_404(customer_review, pk=pk)
        try:
            review.delete()
            messages.success(request, "Review deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting review: {str(e)}")
        
        return redirect('customer_review_list')

class ContactUsListView(View):
    def get(self, request):
        contacts = contact_us.objects.all().order_by('-created_at')
        return render(request, 'Admin/Contact/Contact_List.html', {
            'contacts': contacts,
            'breadcrumb': {'child': 'Contact Us Messages'}
        })

class ContactUsDetailView(View):
    def get(self, request, pk):
        contact_msg = get_object_or_404(contact_us, pk=pk)
        return JsonResponse({
            'id': contact_msg.id,
            'name': contact_msg.name,
            'email': contact_msg.email,
            'subject': contact_msg.subject,
            'message': contact_msg.message,
            'created_at': contact_msg.created_at.strftime('%Y-%m-%d %H:%M') if contact_msg.created_at else None,
            'updated_at': contact_msg.updated_at.strftime('%Y-%m-%d %H:%M') if contact_msg.updated_at else None
        })

class ContactUsEditView(View):
    def get(self, request, pk):
        contact_msg = get_object_or_404(contact_us, pk=pk)
        return JsonResponse({
            'id': contact_msg.id,
            'name': contact_msg.name,
            'email': contact_msg.email,
            'subject': contact_msg.subject,
            'message': contact_msg.message
        })
    
    def post(self, request, pk):
        contact_msg = get_object_or_404(contact_us, pk=pk)
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validation
        if not name:
            messages.error(request, "Name is required")
            return redirect('contact_us_list')
        
        if not email:
            messages.error(request, "Email is required")
            return redirect('contact_us_list')
        
        try:
            contact_msg.name = name
            contact_msg.email = email
            contact_msg.subject = subject
            contact_msg.message = message
            contact_msg.save()
            messages.success(request, "Contact message updated successfully")
        except Exception as e:
            messages.error(request, f"Error updating contact message: {str(e)}")
        
        return redirect('contact_us_list')

class ContactUsDeleteView(View):
    def post(self, request, pk):
        contact_msg = get_object_or_404(contact_us, pk=pk)
        try:
            contact_msg.delete()
            messages.success(request, "Contact message deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting contact message: {str(e)}")
        
        return redirect('contact_us_list')

