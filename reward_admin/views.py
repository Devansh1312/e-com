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
from datetime import datetime, time
from django.http import HttpResponseForbidden, HttpResponseBadRequest,Http404
from django.core.exceptions import ValidationError as DjangoValidationError

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
        if request.user.role.id in [1, 3]:
            return redirect('view_dashboard')
        if request.user.role.id == 4:
            return redirect('Attendance_Taker_Dashboard')
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
                    if user.role_id in [1, 2, 3, 4]:  # All allowed roles
                        login(request, user)
                        if remember_me:
                            request.session.set_expiry(1209600)
                        messages.success(request, "Login Successful")
                        
                        # Redirect based on role
                        if user.role_id == 4:
                            return redirect("Attendance_Taker_Dashboard")
                        return redirect("view_dashboard")
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
        
        # Redirect Ticket Scanners to their specific dashboard
        if request.user.role and request.user.role.id == 4:
            return redirect('Attendance_Taker_Dashboard')
        
        # Total Club Members (assuming role_id=3 are club members)
        total_club_members = User.objects.filter(role_id=3).count()
        
        # Total Sub-Admins (assuming role_id=2 are sub-admins)
        total_sub_admins = User.objects.filter(role_id=2).count()
        
        # Total Ticket Scanners (role_id=4)
        total_attendance_takers = User.objects.filter(role_id=4).count()


        # ========================================
        # CONTEXT PREPARATION
        # ========================================
        
        context = {
            # User Statistics
            'total_club_members': total_club_members,
            'total_sub_admins': total_sub_admins,
            'total_attendance_takers': total_attendance_takers,
        }
        
        return render(request, "Admin/Dashboard.html", context)



############################################## Logout Module ##################################################
def logout_view(request):
    logout(request)
    return redirect("adminlogin")


############################################## List of Club Members ##############################################################
class ClubMemberList(LoginRequiredMixin, View):
    template_name = "Admin/User/Club_Member_List.html"

    def get(self, request):
        # Get parent members for dropdowns
        parent_members = get_user_model().objects.filter(
            role=3,  # Club members
            parent__isnull=True  # Only parent members
        ).order_by('name')
        
        return render(
            request,
            self.template_name,
            {
                "breadcrumb": {"child": "Club Member List"},
                "parent_members": parent_members,
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
            0: 'id',           # Counter (we'll sort by ID for consistent ordering)
            1: 'membership_id',
            2: 'name',
            3: 'email',
            4: 'phone',
            # 5: status (not sortable)
            # 6: actions (not sortable)
        }
        
        # Get the custom user model
        User = get_user_model()
        
        # Base queryset - all club members (role_id=3) with select_related for parent
        queryset = User.objects.filter(role=3).select_related('parent')
        
        # Apply sorting if the column is sortable
        if order_column_index in column_map:
            order_field = column_map[order_column_index]
            if order_direction == 'desc':
                order_field = '-' + order_field
            queryset = queryset.order_by(order_field)
        else:
            # Default ordering if no valid sort column specified
            queryset = queryset.order_by('membership_id')
        
        # Apply search filter if provided
        if search_value:
            queryset = queryset.filter(
                Q(username__icontains=search_value) |
                Q(name__icontains=search_value) |
                Q(email__icontains=search_value) |
                Q(phone__icontains=search_value) |
                Q(membership_id__icontains=search_value)
            )

        # If current user is not admin (role_id=1), filter by cities
        if request.user.role.id != 1:
            user_cities = request.user.cities.all()
            if user_cities:
                queryset = queryset.filter(cities__in=user_cities).distinct()
            else:
                queryset = User.objects.none()

        # Get total records count (without filters)
        if request.user.role.id != 1:
            total_records = User.objects.filter(role=3, cities__in=request.user.cities.all()).count()
        else:
            total_records = User.objects.filter(role=3).count()
        
        # Get filtered count (with search filters applied)
        filtered_records = queryset.count()
        
        # Apply pagination
        members = queryset[start:start + length]
        
        # Prepare data for response
        data = []
        for index, member in enumerate(members):
            status_badge = 'badge-success' if member.is_active else 'badge-danger'
            status_text = 'Active' if member.is_active else 'Inactive'
            
            # Check permissions
            can_edit = request.user.has_permission('club_member_edit')
            can_delete = request.user.has_permission('club_member_delete')
            can_toggle_status = request.user.has_permission('club_member_edit')
            
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
                            <a href="#" class="toggle-status text-decoration-none" data-id="{member.id}" data-status="{'deactivate' if member.is_active else 'activate'}">
                                {'Deactivate' if member.is_active else 'Activate'}
                            </a>
                            <form id="status-form-{member.id}" method="post" action="/club-members/toggle-status/{member.id}/" style="display: none;">
                                <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                                <input type="hidden" name="source_page" value="club_member_list">
                                <input type="hidden" name="title" value="Club Member">
                            </form>
                        </li>
                """
            
            # View action
            actions_html += f"""
                        <li style="padding: 8px 12px; border-bottom: 1px solid #eee; font-size: small;">
                            <a href="/club-member/detail/{member.id}/" class="text-decoration-none">
                                View
                            </a>
                        </li>
            """
            
            # Edit action
            if can_edit:
                edit_url = reverse('club_member_edit', args=[member.id])
                actions_html += f"""
                    <li style="padding: 8px 12px; border-bottom: 1px solid #eee; font-size: small;">
                        <a href="{edit_url}">
                            Edit
                        </a>
                    </li>
                """
            
            # Delete action
            if can_delete:
                actions_html += f"""
                        <li style="padding: 8px 12px; font-size: small;">
                            <a href="#" class="delete-member text-decoration-none" 
                                data-id="{member.id}"
                                data-toggle="modal" 
                                data-target="#deleteClubMemberModal">
                                Delete
                            </a>
                            <form id="delete-form-{member.id}" method="post" action="/club-members/delete/{member.id}/" style="display: none;">
                                <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                                <input type="hidden" name="source_page" value="club_member_list">
                                <input type="hidden" name="title" value="Club Member">
                            </form>
                        </li>
                """
            
            actions_html += """
                    </ul>
                </div>
            </div>
            """
            
            data.append({
                'counter': start + index + 1,
                'membership_id': member.membership_id or 'N/A',
                'name': member.name or 'N/A',
                'email': member.email or 'N/A',
                'phone': member.phone or 'N/A',
                'status': f'<span class="badge {status_badge}">{status_text}</span>',
                'actions': actions_html,
                'parent_id': member.parent.id if member.parent else None,
                'reward_points': member.presidencyclub_balance or 0
            })
        
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data,
        }
        
        return JsonResponse(response) 

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

################### Club Member Edit View #############################
class ClubMemberEditView(LoginRequiredMixin, View):
    template_name = "Admin/User/Club_Member_Edit.html"

    def get(self, request, pk):
        user = get_object_or_404(get_user_model(), pk=pk, role_id=3)
        parent_members = get_user_model().objects.filter(
            role=3,
            parent__isnull=True
        ).order_by('name')
        genders = UserGender.objects.all()
        countries = Country.objects.all()
        states = State.objects.all()
        
        # Format dates properly for display
        formatted_user = {
            'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else '',
            'enrollment_date': user.enrollment_date.strftime('%Y-%m-%d') if user.enrollment_date else '',
            'anniversary_date': user.anniversary_date.strftime('%Y-%m-%d') if user.anniversary_date else '',
        }
        
        return render(
            request,
            self.template_name,
            {
                "breadcrumb": {"parent": "Club Member List", "child": "Edit Club Member"},
                "member": user,
                "formatted_dates": formatted_user,
                "parent_members": parent_members,
                "genders": genders,
                "countries": countries,
                "states": states,
            },
        )

    def post(self, request, pk):
        user = get_object_or_404(get_user_model(), pk=pk, role_id=3)
        data = request.POST
        errors = {}
        parent_members = get_user_model().objects.filter(
            role=3,
            parent__isnull=True
        ).order_by('name')
        genders = UserGender.objects.all()
        countries = Country.objects.all()
        states = State.objects.all()
        
        # Validate required fields
        required_fields = {
            'first_name': 'First name is required',
            'last_name': 'Last name is required',
            'membership_id': 'Membership ID is required',
            'email': 'Email is required',
            'phone': 'Phone number is required',
            'name': 'Full name is required',
        }
        
        for field, error_msg in required_fields.items():
            if not data.get(field):
                errors[field] = [error_msg]
        
        # Membership ID validation
        membership_id = data.get('membership_id')
        if membership_id:
            cleaned_membership_id = membership_id.strip().upper()
            if get_user_model().objects.filter(membership_id=cleaned_membership_id).exclude(pk=user.pk).exists():
                errors['membership_id'] = ['This membership ID is already taken']
        
        # Phone validation
        phone = data.get('phone')
        if phone:
            cleaned_phone = phone.replace(" ", "").replace("-", "")
            if cleaned_phone.startswith('+91'):
                cleaned_phone = cleaned_phone[3:]
            elif cleaned_phone.startswith('91') and len(cleaned_phone) > 10:
                cleaned_phone = cleaned_phone[2:]

            if not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
                errors['phone'] = ['Phone number must be exactly 10 digits']

        # Email validation
        email = data.get('email')
        if email:
            try:
                validate_email(email)
                if get_user_model().objects.filter(email=email).exclude(pk=user.pk).exists():
                    errors['email'] = ['Email already exists']
            except ValidationError:
                errors['email'] = ['Enter a valid email address']
        
        # Track if password is being changed
        password_changed = False
        new_password = None
        
        # Password validation only if provided
        if data.get('password') or data.get('confirm_password'):
            if not data.get('password'):
                errors['password'] = ['Password is required']
            elif len(data.get('password')) < 8:
                errors['password'] = ['Password must be at least 8 characters']
            
            if not data.get('confirm_password'):
                errors['confirm_password'] = ['Please confirm your password']
            elif data.get('password') != data.get('confirm_password'):
                errors['confirm_password'] = ['Passwords do not match']
            else:
                password_changed = True
                new_password = data.get('password')
        
        # Date validation
        date_of_birth = data.get('date_of_birth')
        enrollment_date = data.get('enrollment_date')
        anniversary_date = data.get('anniversary_date')
        
        try:
            if date_of_birth:
                datetime.strptime(date_of_birth, '%Y-%m-%d')
            if enrollment_date:
                datetime.strptime(enrollment_date, '%Y-%m-%d')
            if anniversary_date:
                datetime.strptime(anniversary_date, '%Y-%m-%d')
        except ValueError:
            if date_of_birth:
                errors['date_of_birth'] = ['Enter a valid date (YYYY-MM-DD)']
            if enrollment_date:
                errors['enrollment_date'] = ['Enter a valid date (YYYY-MM-DD)']
            if anniversary_date:
                errors['anniversary_date'] = ['Enter a valid date (YYYY-MM-DD)']
        
        parent_id = data.get('parent_id')
        reward_points = data.get('reward_points', 0)
        
        if not parent_id and not reward_points.isdigit():
            errors['reward_points'] = ['Please enter valid reward points']
        elif not parent_id and int(reward_points) < 0:
            errors['reward_points'] = ['Reward points cannot be negative']

        if errors:
            return render(
                request,
                self.template_name,
                {
                    "breadcrumb": {"parent": "Club Member List", "child": "Edit Club Member"},
                    "member": user,
                    "parent_members": parent_members,
                    "genders": genders,
                    "countries": countries,
                    "states": states,
                    "errors": errors,
                    "form_data": data,
                },
            )
        
        try:
            new_parent = get_user_model().objects.get(pk=parent_id) if parent_id else None
            
            # Update user details
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.membership_id = cleaned_membership_id if membership_id else user.membership_id
            user.date_of_birth = date_of_birth if date_of_birth else user.date_of_birth
            user.anniversary_date = anniversary_date if anniversary_date else user.anniversary_date
            user.address = data.get('address', user.address)
            user.email = email
            user.phone = cleaned_phone if phone else user.phone
            user.name = data.get('name')
            user.gender_id = data.get('gender') if data.get('gender') else user.gender_id
            user.enrollment_date = enrollment_date if enrollment_date else user.enrollment_date
            user.parent = new_parent

            # Update password if provided
            if password_changed:
                user.password = make_password(new_password)
            
            # Handle reward points if this is now a parent user
            if not new_parent and reward_points:
                if user.presidencyclub_balance != int(reward_points):
                    difference = int(reward_points) - user.presidencyclub_balance
                    user.presidencyclub_balance = int(reward_points)
                    
            user.save()
            
            # Send password change email if password was changed
            if password_changed:
                system_settings = SystemSettings.objects.first()
                send_password_change_email(
                    email=user.email,
                    membership_id=user.membership_id,
                    name=user.name,
                    password=new_password,
                    system_settings=system_settings,
                    request=request
                )

            messages.success(request, 'Club member updated successfully')
            return redirect('club_member_list')
            
        except Exception as e:
            messages.error(request, f'Error updating club member: {str(e)}')
            return render(
                request,
                self.template_name,
                {
                    "breadcrumb": {"parent": "Club Member List", "child": "Edit Club Member"},
                    "member": user,
                    "parent_members": parent_members,
                    "genders": genders,
                    "countries": countries,
                    "states": states,
                    "errors": {'general': [str(e)]},
                    "form_data": data,
                },
            )

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

# Club Member Toggle Status View
class ClubMemberToggleStatusView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, role_id=3)
        try:
            user.is_active = not user.is_active
            user.save()
            
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f'Club member {status} successfully')
            return JsonResponse({
                'success': True
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error toggling status: {str(e)}'
            }, status=500)

##################################### Club Member Delete View ##############################################
class ClubMemberDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy('club_member_list')
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for deleting a club member and their children"""
        self.object = self.get_object()
        
        try:
            # Store member details before deletion
            member_name = self.object.name
            
            # Delete all child members recursively
            self.delete_children(self.object)
            
            # Delete the parent member
            self.object.delete()
            
            # Set success message
            success_msg = f"Member '{member_name}' and all associated members have been successfully deleted!"
            messages.success(request, success_msg)
            
        except Exception as e:
            # Set error message
            error_msg = f"Error deleting member: {str(e)}"
            messages.error(request, error_msg)
        
        # Always redirect to success URL
        return redirect(self.success_url)
    
    def delete_children(self, user):
        """Recursively delete all children of a user"""
        children = User.objects.filter(parent=user)
        for child in children:
            # Recursively delete the child's children first
            self.delete_children(child)
            # Then delete the child
            child.delete()
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - redirect with error message"""
        error_msg = 'Invalid request method. Use POST to delete a member.'
        messages.error(request, error_msg)
        return redirect(self.success_url)


################################## SytemSettings view #######################################################
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

        fs = FileSystemStorage(
            location=os.path.join(settings.MEDIA_ROOT, "System_Settings")
        )

        errors = {}
        success = False

        try:
            # Handle file uploads
            file_fields = {
                "fav_icon": "fav_icon",
                "website_logo": "website_logo",
            }

            for field_name, field_label in file_fields.items():
                if field_name in request.FILES:
                    field_file = request.FILES[field_name]
                    current_file = getattr(system_settings, field_label, None)

                    # Remove old file if it exists
                    if current_file:
                        old_file_path = os.path.join(settings.MEDIA_ROOT, current_file)
                        if os.path.isfile(old_file_path):
                            os.remove(old_file_path)

                    # Generate a unique filename and store the file
                    file_extension = field_file.name.split(".")[-1]
                    unique_suffix = get_random_string(8)
                    file_filename = f"system_settings/{field_label}_{unique_suffix}.{file_extension}"
                    
                    # Save the file using default storage
                    image_path = default_storage.save(file_filename, field_file)
                    
                    # Update the system_settings with the new file path
                    setattr(system_settings, field_label, image_path)

            # Handle required fields
            required_fields = {
                "phone": "Phone number is required",
            }

            for field, error_message in required_fields.items():
                field_value = request.POST.get(field)
                if not field_value:
                    errors[field] = error_message
                else:
                    setattr(system_settings, field, field_value)

            # Handle optional fields
            optional_fields = [
                "email",
                "club_address",
                "office_address",
                "website_name",
                "gst_number",
                "razorpay_key",
                "razorpay_secret",
            ]

            for field in optional_fields:
                field_value = request.POST.get(field)
                setattr(system_settings, field, field_value)
            
            if not errors:
                system_settings.save()
                success = True
                messages.success(request, "System settings updated successfully.")
            else:
                messages.error(request, "Please correct the errors below.")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        if errors:
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
        return redirect("System_Settings")


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


##################################################### User Update Profile View ###############################################################
class UserUpdateProfileView(View):
    def get(self, request, *args, **kwargs):
        countries = Country.objects.all()
        cities = City.objects.all()
        
        return render(
            request,
            "Admin/User/Edit_Profile.html",
            {
                "user": request.user,
                "countries": countries,
                "cities": cities,
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
            cities_ids = request.POST.getlist('cities')
            
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
            
            if cities_ids:
                try:
                    cities = City.objects.filter(id__in=cities_ids)
                    if cities.count() != len(cities_ids):
                        errors['cities'] = ['One or more invalid cities selected']
                    else:
                        # Validate that all cities belong to selected state
                        if user.state:
                            invalid_cities = cities.exclude(state=user.state)
                            if invalid_cities.exists():
                                errors['cities'] = ['One or more cities do not belong to selected state']
                            else:
                                user.cities.set(cities)
                        else:
                            errors['cities'] = ['Please select a state first']
                except ValueError:
                    errors['cities'] = ['Invalid cities selected']
            else:
                user.cities.clear()
        
        # Handle file uploads (keep your existing code)
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

        # Handle card header (similar validation)
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

class SubAdminList(LoginRequiredMixin, View):
    template_name = "Admin/User/Sub_Admin_List.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "breadcrumb": {"child": "Sub Admin List"},
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
            0: 'id',           # Counter (we'll sort by ID for consistent ordering)
            1: 'username',
            2: 'name',
            3: 'email',
            4: 'phone',
            # 5: cities (not sortable)
            # 6: status (not sortable)
            # 7: actions (not sortable)
        }
        
        # Get the custom user model
        User = get_user_model()
        
        # Base queryset - all sub admins (role_id=2)
        queryset = User.objects.filter(role=2)
        
        # Apply sorting if the column is sortable
        if order_column_index in column_map:
            order_field = column_map[order_column_index]
            if order_direction == 'desc':
                order_field = '-' + order_field
            queryset = queryset.order_by(order_field)
        else:
            # Default ordering if no valid sort column specified
            queryset = queryset.order_by('name')
        
        # Apply search filter if provided
        if search_value:
            queryset = queryset.filter(
                Q(username__icontains=search_value) |
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
        total_records = User.objects.filter(role=2).count()
        
        # Get filtered count (with search filters applied)
        filtered_records = queryset.count()
        
        # Apply pagination
        members = queryset[start:start + length]
        
        # Prepare data for response
        data = []
        for index, member in enumerate(members):
            status_badge = 'badge-success' if member.is_active else 'badge-danger'
            status_text = 'Active' if member.is_active else 'Inactive'
            
            # Get assigned cities
            cities = ", ".join([city.name for city in member.cities.all()[:3]])
            if member.cities.count() > 3:
                cities += f" (+{member.cities.count() - 3} more)"
            
            # Check permissions
            can_edit = request.user.has_permission('sub_admin_edit')
            can_delete = request.user.has_permission('sub_admin_delete')
            can_toggle_status = request.user.has_permission('sub_admin_edit')
            
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
                            <a href="#" class="toggle-status text-decoration-none" data-id="{member.id}" data-status="{'deactivate' if member.is_active else 'activate'}">
                                {'Deactivate' if member.is_active else 'Activate'}
                            </a>
                            <form id="status-form-{member.id}" method="post" action="/sub-admin/toggle-status/{member.id}/" style="display: none;">
                                <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                                <input type="hidden" name="source_page" value="sub_admin_list">
                                <input type="hidden" name="title" value="Sub Admin">
                            </form>
                        </li>
                """
            
            # View action
            actions_html += f"""
                        <li style="padding: 8px 12px; border-bottom: 1px solid #eee; font-size: small;">
                            <a href="/sub-admin/detail/{member.id}/" class="text-decoration-none">
                                View
                            </a>
                        </li>
            """
            
            # Edit action
            if can_edit:
                actions_html += f"""
                        <li style="padding: 8px 12px; border-bottom: 1px solid #eee; font-size: small;">
                            <a href="/sub-admin/edit/{member.id}/" class="text-decoration-none">
                                Edit
                            </a>
                        </li>
            """
            
            # Delete action
            if can_delete:
                actions_html += f"""
                    <li>
                        <a href="#" class="text-decoration-none delete-subadmin" 
                            data-id="{member.id}"
                            data-toggle="modal" 
                            data-target="#deleteSubAdminModal">
                            Delete
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
                'username': member.username or 'N/A',
                'name': member.name or 'N/A',
                'email': member.email or 'N/A',
                'phone': member.phone or 'N/A',
                'cities': cities or 'N/A',
                'status': f'<span class="badge {status_badge}">{status_text}</span>',
                'actions': actions_html
            })
        
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data,
        }
        
        return JsonResponse(response)

######################################## Sub Admin Detail Page #################################################        
class SubAdminDetailView(LoginRequiredMixin, View):
    template_name = "Admin/User/SubAdmin_Detail.html"

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk, role_id=2)  # Ensure it's a sub-admin
            
            # Get basic information only
            return render(
                request,
                self.template_name,
                {
                    "user": user,
                    "title": "Sub Admin Details",
                },
            )
        except User.DoesNotExist:
            return redirect("sub_admin_list")

    def post(self, request, pk):
        return self.get(request, pk)
######################################### Sub Admin Create View ######################################################
######################################### Sub Admin Create View ######################################################
class SubAdminCreateView(View):
    template_name = "Admin/User/Sub_Admin_Create.html"
    
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Get all states for the dropdown
        states = State.objects.all().order_by('name')
        
        context = {
            'states': states,
            'breadcrumb': {'child': 'Add Sub Admin'}
        }
        return render(request, self.template_name, context)
    
    def validate_phone(self, phone):
        """Validate and clean phone number"""
        if not phone:
            return None, "Phone number is required"
            
        cleaned_phone = phone.replace(" ", "").replace("-", "")
        
        # Handle country code prefixes
        if cleaned_phone.startswith('+91'):
            cleaned_phone = cleaned_phone[3:]
        elif cleaned_phone.startswith('91') and len(cleaned_phone) > 10:
            cleaned_phone = cleaned_phone[2:]
        
        # Validate digits and length
        if not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
            return None, "Phone number must be exactly 10 digits"
            
        # Check if phone already exists
        if User.objects.filter(phone=cleaned_phone).exists():
            return None, "Phone number already exists"
            
        return cleaned_phone, None
    
    def validate_form_data(self, data):
        """Validate all form data and return errors if any"""
        errors = {}
        
        # Name validation
        if not data.get('name'):
            errors['name'] = ['Name is required']
        elif len(data.get('name', '')) > 50:  # Add reasonable length limit
            errors['name'] = ['Name cannot exceed 50 characters']
        
        # Email validation
        email = data.get('email')
        if not email:
            errors['email'] = ['Email is required']
        else:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors['email'] = ['Email already exists']
            except DjangoValidationError:
                errors['email'] = ['Enter a valid email address']
        
        # Phone validation
        phone = data.get('phone')
        cleaned_phone, phone_error = self.validate_phone(phone)
        if phone_error:
            errors['phone'] = [phone_error]
        
        # State validation
        state_id = data.get('state')
        if not state_id:
            errors['state'] = ['State is required']
        else:
            try:
                State.objects.get(id=state_id)
            except State.DoesNotExist:
                errors['state'] = ['Invalid state selected']
        
        # Cities validation
        cities = data.getlist('cities')
        if not cities:
            errors['cities'] = ['At least one city must be selected']
        else:
            # Validate that cities belong to the selected state
            if state_id:
                valid_city_ids = City.objects.filter(state_id=state_id).values_list('id', flat=True)
                for city_id in cities:
                    if int(city_id) not in valid_city_ids:
                        errors['cities'] = ['Invalid city selection for the selected state']
                        break
        
        # Password validation
        password = data.get('password')
        if not password:
            errors['password'] = ['Password is required']
        elif len(password) < 8:
            errors['password'] = ['Password must be at least 8 characters']
        
        # Confirm password validation
        confirm_password = data.get('confirm_password')
        if not confirm_password:
            errors['confirm_password'] = ['Please confirm your password']
        elif password != confirm_password:
            errors['confirm_password'] = ['Passwords do not match']
        
        return errors, cleaned_phone
    
    def create_subadmin_user(self, data, cleaned_phone):
        """Create the subadmin user with provided data"""
        return User.objects.create(
            username=data.get('email'),
            membership_id=data.get('email'),
            email=data.get('email'),
            name=data.get('name'),
            phone=cleaned_phone,
            password=make_password(data.get('password')),
            role_id=2,  # Sub Admin role
            country_id=1,  # Fixed country
            state_id=data.get('state'),
            register_type='Admin',  # Assuming admin created
            is_active=True
        )
    
    def post(self, request):
        data = request.POST
        
        # Get states for re-rendering the form if there are errors
        states = State.objects.all().order_by('name')
        
        # Validate form data
        errors, cleaned_phone = self.validate_form_data(data)
        
        if errors:
            # Return the form with errors displayed
            return render(request, self.template_name, {
                'states': states,
                'breadcrumb': {'child': 'Add Sub Admin'},
                'errors': errors,
                'form_data': {
                    'name': data.get('name'),
                    'email': data.get('email'),
                    'phone': data.get('phone'),
                    'state': data.get('state'),
                    'cities': data.getlist('cities'),
                }
            })
        
        try:
            # Create the user
            user = self.create_subadmin_user(data, cleaned_phone)
            
            # Add cities
            cities = data.getlist('cities')
            user.cities.set(cities)
            
            # Send welcome email
            email_sent = self.send_welcome_email(user, data.get('password'))
            if not email_sent:
                # Log warning but don't fail the creation
                pass  # You might want to add logging here
            
            messages.success(request, 'Sub admin created successfully')
            return redirect('sub_admin_list')
            
        except Exception as e:
            # If there's an error during creation, show it on the form
            errors['general'] = [f'Error creating sub admin: {str(e)}']
            return render(request, self.template_name, {
                'states': states,
                'breadcrumb': {'child': 'Add Sub Admin'},
                'errors': errors,
                'form_data': {
                    'name': data.get('name'),
                    'email': data.get('email'),
                    'phone': data.get('phone'),
                    'state': data.get('state'),
                    'cities': data.getlist('cities'),
                }
            })
    
    def send_welcome_email(self, user, password):
        """Send welcome email to the new subadmin"""
        try:
            system_settings = SystemSettings.objects.first()
            logo = system_settings.website_logo if system_settings and system_settings.website_logo else ''
            logo_url = f"{settings.MEDIA_DOMAIN}{logo}" if logo else ''
            website_name = system_settings.website_name if system_settings else 'Baroda Presidency Club'
            
            # Prepare context for email template
            context = {
                'name': user.name,
                'current_year': datetime.now().year,
                'email': user.email,
                'password': password,
                'logo': logo_url,
                'static_url': settings.STATIC_DOMAIN,
                'website_name': website_name,
                'login_url': settings.DOMAIN
            }
            
            email_content = render_to_string('emails/subadmin_welcome_email.html', context)
            
            # Send the email
            subject = 'Welcome as Sub Admin'
            send_mail(
                subject=subject,
                message=f'Welcome {user.name} as Sub Admin to {website_name}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=email_content,
                fail_silently=False,
            )
            return True
            
        except Exception as e:
            # Log the error but don't break the user creation process
            # You might want to add proper logging here
            return False

######################################### Sub Admin Edit View ######################################################
class SubAdminEditView(View):
    template_name = "Admin/User/Sub_Admin_Edit.html"
    
    def get(self, request, pk):
        # Get the sub admin user
        sub_admin = get_object_or_404(User, pk=pk, role_id=2)
        
        # Get all states for the dropdown
        states = State.objects.all().order_by('name')
        
        return render(request, self.template_name, {
            'sub_admin': sub_admin,
            'states': states,
            'breadcrumb': {'child': 'Edit Sub Admin'}
        })
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, role_id=2)
        data = request.POST
        errors = {}
        
        # Validate required fields
        if not data.get('name'):
            errors['name'] = ['Name is required']
        
        if not data.get('email'):
            errors['email'] = ['Email is required']
        
        phone = data.get('phone') or request.POST.get('phone')
        if not phone:
            errors['phone'] = ['Phone number is required']
        else:
            # Phone number validation (same as club member)
            cleaned_phone = phone.replace(" ", "").replace("-", "")
            if cleaned_phone.startswith('+91'):
                cleaned_phone = cleaned_phone[3:]
            elif cleaned_phone.startswith('91') and len(cleaned_phone) > 10:
                cleaned_phone = cleaned_phone[2:]
            if not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
                errors['phone'] = ['Phone number must be exactly 10 digits']
        
        if not data.get('state'):
            errors['state'] = ['State is required']
        
        if not data.get('cities'):
            errors['cities'] = ['At least one city must be selected']
        
        # Validate email format and uniqueness
        try:
            validate_email(data.get('email'))
            if User.objects.filter(email=data.get('email')).exclude(pk=user.pk).exists():
                errors['email'] = ['Email already exists']
        except ValidationError:
            errors['email'] = ['Enter a valid email address']
        
        # Password validation only if provided
        if data.get('password') or data.get('confirm_password'):
            if not data.get('password'):
                errors['password'] = ['Password is required']
            elif len(data.get('password')) < 8:
                errors['password'] = ['Password must be at least 8 characters']
            
            if not data.get('confirm_password'):
                errors['confirm_password'] = ['Please confirm your password']
            elif data.get('password') != data.get('confirm_password'):
                errors['confirm_password'] = ['Passwords do not match']
        
        if errors:
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please correct the errors below'
            }, status=400)
        
        try:
            # Update user details
            user.email = data.get('email')
            user.username = data.get('email')  # Keep username in sync with email
            user.membership_id = data.get('email')  # Keep membership_id in sync with email
            user.name = data.get('name')
            user.phone = cleaned_phone
            user.state_id = data.get('state')
            
            # Update password if provided
            if data.get('password'):
                user.password = make_password(data.get('password'))
            
            user.save()
            
            # Update cities
            cities = data.getlist('cities')
            user.cities.set(cities)
            
            messages.success(request, 'Sub admin updated successfully')
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('sub_admin_list')
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating sub admin: {str(e)}'
            }, status=400)



############################## Sub Admin Toggle Status View ###################################
class SubAdminToggleStatusView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, role_id=2)
        try:
            user.is_active = not user.is_active
            user.save()
            
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f'Sub admin {status} successfully')
            return JsonResponse({
                'success': True
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error toggling status: {str(e)}'
            }, status=500)

########################### Sub Admin Delete View #################################
class SubAdminDeleteView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, role_id=2)  # Assuming role_id=2 is for sub-admins
        try:
            email = user.email
            user.delete()
            messages.success(request, f'Sub admin deleted successfully')
            return JsonResponse({
                'success': True,
                'message': 'Sub admin deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deleting sub admin: {str(e)}'
            }, status=500)
        
    
################## Send OTP for Forgot Password Email ##################################
def send_forgot_password_otp(email, otp, system_settings, subject, request, is_admin=False):
    try:
        logo = system_settings.website_logo if system_settings and system_settings.website_logo else ''
        logo_url = f"{settings.MEDIA_DOMAIN}{logo}" if logo else ''
        static_url = f"{settings.STATIC_DOMAIN}"
        website_name = system_settings.website_name if system_settings else 'Presidency Club'
        
        # Prepare context for email template
        context = {
            'otp': otp,
            'current_year': datetime.now().year,
            'logo': logo_url,
            'static_url': static_url,
            'is_admin': is_admin,  # Add flag to identify admin emails
            'website_name': website_name
        }
        
        # Use different templates for admin vs regular users
        template_name = 'emails/forgot_password_otp_admin.html'
        email_content = render_to_string(template_name, context)
        
        # Send the email
        send_mail(
            subject=subject,
            message=f'Your password reset OTP is: {otp}',  # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=email_content,
            fail_silently=False,
        )
        return True
        
    except Exception as e:
        return False
    
# Send OTP for Sub Admin Email
class ForgotPasswordAdminView(View):
    template_name = "Admin/Forgot_Password_Admin.html"
    success_url_name = "verify_otp_admin"
    fail_url_name = "Forgot_Password_Admin"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Email address is required.")
            return redirect(self.fail_url_name)

        try:
            user = User.objects.get(email=email, is_active=True, role_id__in=[1,2,4])
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            system_settings = SystemSettings.objects.first()
            if not system_settings:
                messages.error(request, "System error. Please contact support.")
                return redirect(self.fail_url_name)
            
            subject = 'Admin Password Reset Verification Code'

            email_sent = send_forgot_password_otp(
                email=email,
                otp=otp,
                system_settings=system_settings,
                subject=subject,
                request=request,
                is_admin=True  # Pass the admin flag
            )
        
            # Production note: Uncomment the following lines to handle email sending errors
            if email_sent:
                request.session['reset_password_email'] = email
                messages.success(request, "A verification code has been sent to your email.")
                return redirect(self.success_url_name)
            
            # If email failed to send
            user.otp = None
            user.otp_created_at = None
            user.save()
            messages.error(request, "Failed to send verification email. Please try again.")
            return redirect(self.fail_url_name)
            
        except User.DoesNotExist:
            # Don't reveal whether user exists or not
            messages.error(request, "If this email is registered, you'll receive a verification code.")
            return redirect(self.fail_url_name)
        except Exception as e:
            print(f"Error in ForgotPasswordAdminView: {str(e)}")
            messages.error(request, "An error occurred. Please try again.")
            return redirect(self.fail_url_name)

# Verify OTP for Forgot Password Email
class VerifyOTPAdminView(View):
    template_name = "Admin/Verify_OTP_Admin_Forgot_Password.html"
    login_url_name = "reset_password_admin"  # Change this to your admin login URL name
    otp_expiry_minutes = 10  # OTP expires after 10 minutes

    def get(self, request, email=None):
        # Check if email is in session (from forgot password flow)
        email = email or request.session.get('reset_password_email')
        if not email:
            messages.error(request,"Password reset session expired. Please start again.")
            return redirect('Forgot_Password_Admin')
        
        return render(request, self.template_name, {
            'email': email,
            'partial_email': self._obfuscate_email(email)
        })

    def post(self, request):
        email = request.session.get('reset_password_email')
        if not email:
            messages.error(request, "Session expired. Please request a new OTP.")
            return redirect('Forgot_Password_Admin')

        # Try hidden field, fallback to combining from inputs
        otp = request.POST.get('full_otp', '').strip()
        if not otp:
            otp = ''.join([request.POST.get(f'otp_{i}', '').strip() for i in range(1, 7)])

        if not otp or len(otp) != 6 or not otp.isdigit():
            messages.error(request, "Please enter a valid 6-digit OTP.")
            return self._render_error_response(request, email)

        try:
            user = User.objects.get(
                email=email,
                is_active=True,
                role_id__in=[1,2,4]  # Admin or Sub-Admin roles
            )

            if (user.otp != otp or 
                not user.otp_created_at or
                (timezone.now() - user.otp_created_at).total_seconds() > self.otp_expiry_minutes * 60):
                messages.error(request, "Invalid or expired OTP. Please request a new one.")
                request.session['reset_password_email'] = email  # Keep the email in session for retry
                return self._render_error_response(request, email)

            # OTP is valid - store verification in session
            request.session['otp_verified'] = True
            request.session['reset_user_id'] = str(user.id)
            
            # Clear the OTP after successful verification
            user.otp = None
            user.otp_created_at = None
            user.save()

            messages.success(request, "OTP verified successfully. You can now reset your password.")
            return redirect(self.login_url_name)

        except User.DoesNotExist:
            messages.error(request, "User not found. Please try again.")
            return redirect('Forgot_Password_Admin')
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            return self._render_error_response(request, email)


    def _render_error_response(self, request, email):
        """Helper method to render the error response with the same context as get"""
        
        return render(request, self.template_name, {
            'email': email,
            'partial_email': self._obfuscate_email(email)
        })

    def _obfuscate_email(self, email):
        """Helper method to partially obscure the email for display"""
        if '@' not in email:
            return email
        name, domain = email.split('@', 1)
        if len(name) > 3:
            obscured = name[:2] + '*' * (len(name)-2) + '@' + domain
        else:
            obscured = name[0] + '*' * (len(name)-1) + '@' + domain
        return obscured


class ResetPasswordAdminView(View):
    template_name = "Admin/Reset_Password_Admin.html"
    success_url_name = "adminlogin"  # URL name for admin login
    session_key = 'reset_user_id'

    def get(self, request):
        # Check if OTP was verified
        if not request.session.get('otp_verified'):
            messages.error(request, "OTP verification required first.")
            return redirect('Forgot_Password_Admin')
            
        user_id = request.session.get(self.session_key)
        if not user_id:
            messages.error(request, "Session expired. Please start again.")
            return redirect('Forgot_Password_Admin')

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('Forgot_Password_Admin')

        
        return render(request, self.template_name)

    def post(self, request):
        if not request.session.get('otp_verified'):
            messages.error(request, "OTP verification required first.")
            return redirect('Forgot_Password_Admin')

        user_id = request.session.get(self.session_key)
        if not user_id:
            messages.error(request, "Session expired. Please start again.")
            return redirect('Forgot_Password_Admin')

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic password validation
        if not password or not confirm_password:
            messages.error(request, "Please fill in all fields.")
            return render(request, self.template_name)
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name)
            
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, self.template_name)

        try:
            user = User.objects.get(id=user_id, is_active=True)
            user.password = make_password(password)
            user.save()
            
            # Clear session variables
            request.session.pop('otp_verified', None)
            request.session.pop(self.session_key, None)
            request.session.pop('reset_password_email', None)

            messages.success(request, "Password changed successfully. Please login with your new password.")
            return redirect(self.success_url_name)
            
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('Forgot_Password_Admin')
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            return render(request, self.template_name)



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




########################## Brand Tie-Up Management Views ###########################################
def generate_unique_filename(prefix, extension):
    """Generate a unique filename with timestamp"""
    import uuid
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}.{extension}"
