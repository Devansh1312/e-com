# ========================================
# Python Standard Library Dependencies
# ========================================
import os
import random
import string
import time
import base64
from io import BytesIO
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from django.core.cache import cache

# ========================================
# Django Core Framework Imports
# ========================================
from django.conf import settings
from django.db import transaction
from django.db.models import Sum, Q
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.files.storage import default_storage
from django.contrib.auth.hashers import make_password
from django.core.paginator import EmptyPage
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_date
from django.views import View

# ========================================
# Django REST Framework (DRF) Imports
# ========================================
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

# ========================================
# Third-Party Library Imports
# ========================================
from rest_framework_simplejwt.tokens import RefreshToken
import qrcode
from weasyprint import HTML
from xhtml2pdf import pisa

# ========================================
# Application-Specific Imports
# ========================================
from reward_admin.models import *
from reward_api.serializers import *


############# Custom Pagination #############################
class CustomPagination(PageNumberPagination):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        try:
            page_number = request.query_params.get(self.page_query_param, 1)
            self.page = int(page_number)
            if self.page < 1:
                raise ValidationError("Page number must be a positive integer.")
        except (ValueError, TypeError):
            return Response({
                'status': 0,
                'message': 'Page not found.',
                'data': []
            }, status=400)

        paginator = self.django_paginator_class(queryset, self.get_page_size(request))
        self.total_pages = paginator.num_pages
        self.total_records = paginator.count

        try:
            page = paginator.page(self.page)
        except EmptyPage:
            return Response({
                'status': 0,
                'message': 'Page not found.',
                'data': []
            }, status=400)

        self.paginated_data = page
        return list(page)

    def get_paginated_response(self, data):
        return Response({
            'status': 1,
            'message':'Data fetched successfully.',
            'total_records': self.total_records,
            'total_pages': self.total_pages,
            'current_page': self.page,
            'data': data
        })
##################### User Registration Send OTP #####################
class SendRegistrationOTP(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        phone = request.data.get('phone')
        
        if not email:
            return Response({
                'status': 0,
                'message': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not phone:
            return Response({
                'status': 0,
                'message': 'Mobile Number is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if email already exists in User model
        if User.objects.filter(email=email).exists():
            return Response({
                'status': 0,
                'message': 'Email already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if Mobile Number already exists in User model
        if User.objects.filter(phone=phone).exists():
            return Response({
                'status': 0,
                'message': 'Mobile Number already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate 4-digit OTP
        otp = str(random.randint(1000, 9999))
        
        # Delete any existing OTP for this email
        OTPSave.objects.filter(email=email).delete()
        
        # Save OTP to database
        otp_record = OTPSave.objects.create(
            email=email,
            OTP=otp
        )
        
        try:
            system_settings = SystemSettings.objects.first()
            if not system_settings:
                return Response({
                    'status': 0,
                    'message': 'System configuration error. Please contact support.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            email_sent = send_registration_otp(
                email=email,
                otp=otp,
                system_settings=system_settings,
                subject='Registration Verification OTP',
                request=request
            )
            
            # Production note: Uncomment the following lines to handle email sending errors
            if not email_sent:
                # Delete the OTP record if email fails to send
                otp_record.delete()
                return Response({
                    'status': 0,
                    'message': 'Failed to send OTP email.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'status': 1,
                'message': 'OTP sent successfully.',
                'data': {
                    # 'email': email,  
                    # 'otp': otp_record.OTP  
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Delete the OTP record if email fails to send
            otp_record.delete()
            return Response({
                'status': 0,
                'message': 'Failed to send OTP email.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_registration_otp(email, otp, system_settings, subject, request):
    try:
        logo = system_settings.website_logo if system_settings and system_settings.website_logo else ''
        logo_url = f"{settings.MEDIA_DOMAIN}{logo}" if logo else ''
        static_url = f"{settings.STATIC_DOMAIN}"
        website_name = system_settings.website_name if system_settings and system_settings.website_name else 'Presidency Club'

        # Prepare context for email template
        context = {
            'otp': otp,
            'current_year': datetime.now().year,
            'logo': logo_url,
            'static_url': static_url,
            'website_name': website_name,
            'request': request,  # Pass request to the template if needed
        }
        
        email_content = render_to_string('emails/registration_otp.html', context)
        
        # Send the email
        send_mail(
            subject=subject,
            message=f'Your registration OTP is: {otp}',  # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=email_content,
            fail_silently=False,
        )
        return True
        
    except Exception as e:
        print(f"Failed to send registration OTP email: {str(e)}")
        return False
####################### Verify OTP and Register User #####################
class VerifyOTPAndRegister(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def generate_membership_id(self, parent_id=None):
        current_year = timezone.now().year
        
        if parent_id:
            # This is a child member - use parent's family number and increment member number
            parts = parent_id.split('/')
            family_number = parts[2]
            
            # Find the highest member number for this family
            last_member = User.objects.filter(
                membership_id__startswith=f"FM/{current_year}/{family_number}/"
            ).order_by('-membership_id').first()
            
            if last_member:
                last_number = int(last_member.membership_id.split('/')[3])
                new_number = last_number + 1
            else:
                new_number = 1
                
            return f"FM/{current_year}/{family_number}/{new_number:02d}"
        else:
            # This is a parent member - create new family number
            # Find the last family number for this year
            last_family = User.objects.filter(
                membership_id__regex=r'FM/' + str(current_year) + r'/\d{4}/01$'
            ).order_by('-membership_id').first()
            
            if last_family:
                last_family_number = int(last_family.membership_id.split('/')[2])
                new_family_number = last_family_number + 1
            else:
                new_family_number = 1
                
            return f"FM/{current_year}/{new_family_number:04d}/01"

    def post(self, request, *args, **kwargs):
        # Get all required fields
        full_name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        date_of_birth = request.data.get('date_of_birth')
        password = request.data.get('password')
        otp = request.data.get('otp')
        parent_membership_id = request.data.get('parent_membership_id') or None

        # Validate required fields
        if not all([full_name, email, phone, date_of_birth, password, otp]):
            return Response({
                'status': 0,
                'message': 'All fields are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Split full name into first and last name
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Check if email already exists in User model
        if User.objects.filter(email=email).exists():
            return Response({
                'status': 0,
                'message': 'Email already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if Mobile Number already exists in User model
        if User.objects.filter(phone=phone).exists():
            return Response({
                'status': 0,
                'message': 'Mobile Number already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        try:
            otp_record = OTPSave.objects.get(email=email)
        except OTPSave.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'OTP not found for this email.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ##### For Testing Purpose
        if otp not in ['1234', 1234]:
            return Response({
                'status': 0,
                'message': 'Invalid OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # For Production
        # if otp_record.OTP != otp:
        #     return Response({
        #         'status': 0,
        #         'message': 'Invalid OTP.'
        #     }, status=status.HTTP_400_BAD_REQUEST)

        # # Check if OTP is expired (assuming 5 minutes validity)
        # if timezone.now() > otp_record.created_at + timedelta(minutes=5):
        #     return Response({
        #         'status': 0,
        #         'message': 'OTP has expired.'
        #     }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate membership ID
            membership_id = self.generate_membership_id(parent_membership_id)
            
            # Find parent user if provided
            parent_user = None
            if parent_membership_id:
                parent_user = User.objects.filter(membership_id=parent_membership_id).first()
                if not parent_user:
                    return Response({
                        'status': 0,
                        'message': 'Parent member not found.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Create the user
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=membership_id,
                email=email,
                phone=phone,
                name=full_name,
                password=make_password(password),
                date_of_birth=date_of_birth if date_of_birth else None,
                is_active=True,
                register_type='Mobile App',
                membership_id=membership_id,
                parent=parent_user,
                role_id=3,   # Club Member role
                # Use parent's dates if this is a child member
                enrollment_date=parent_user.enrollment_date if parent_user else None,
                anniversary_date=parent_user.anniversary_date if parent_user else None
            )

            # Delete the OTP record after successful registration
            otp_record.delete()

            # Generate tokens for immediate login
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user, context={'request': request})

            return Response({
                'status': 1,
                'message': 'Registration successful.',
                'data': {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    **serializer.data
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred during registration.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################### Login API ###############################
class LoginAPI(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        
        try:
            login_input = request.data.get('email')  # Could be email or membership ID
            password = request.data.get('password')
            device_type = request.data.get('device_type')
            device_token = request.data.get('device_token')

            if not login_input or not password:
                return Response({
                    'status': 0,
                    'message': 'Membership ID and password are required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not device_type and not device_token:
                return Response({
                    'status': 0,
                    'message': 'Device type and token are required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if device_type not in ['1', '2', 1, 2]:
                return Response({
                    'status': 0,
                    'message': 'Invalid device type.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Try to authenticate by email or membership ID
            try:
                user = User.objects.get(membership_id=login_input)
            except User.DoesNotExist:
                return Response({
                    'status': 0,
                    'message': 'Invalid credentials.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_password(password):
                return Response({
                    'status': 0,
                    'message': 'Invalid credentials.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if user.role_id != 3:
                return Response({
                    'status': 0,
                    'message': 'Invalid credentials.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({
                    'status': 0,
                    'message': 'Account is not active.'
                }, status=status.HTTP_400_BAD_REQUEST)

            user.last_login = timezone.now()
            user.device_type = device_type
            user.device_token = device_token
            user.save()

            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user, context={'request': request})
            return Response({
                'status': 1,
                'message': 'Login successful.',
                'data': {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    **serializer.data
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred during login.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################ Logout API ############################      
class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response({
                    'status': 0,
                    'message': 'Refresh token is required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Optional: Clear any device tokens or other session data
            user = request.user
            user.device_token = None  # If you have device token field
            user.save()

            return Response({
                'status': 1,
                'message': 'Successfully logged out.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'Error during logout.',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

############################# Forgot Password API ############################
class ForgotPasswordAPI(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({
                'status': 0,
                'message': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate 4-digit OTP
            otp = str(random.randint(1000, 9999))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            try:
                system_settings = SystemSettings.objects.first()
                if not system_settings:
                    return Response({
                        'status': 0,
                        'message': 'System configuration error. Please contact support.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                email_sent = send_forgot_password_otp(
                    email=email,
                    otp=otp,
                    system_settings=system_settings,
                    subject='Password Reset OTP',
                    request=request
                )

                # Production note: Uncomment the following lines to handle email sending errors
                if not email_sent:
                    return Response({
                        'status': 0,
                        'message': 'We encountered an issue while sending your OTP email. Please try again.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response({
                    'status': 1,
                    'message': 'A verification code has been sent to your email address. Please check your inbox.',
                    'data': {
                        # 'otp': otp
                        }  # Remove this in production
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                # Clear OTP if email fails
                user.otp = None
                user.otp_created_at = None
                user.save()
                
                return Response({
                    'status': 0,
                    'message': 'We were unable to send the verification email. Please try again later.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except User.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'No registered account found with this email address.'
            }, status=status.HTTP_404_NOT_FOUND)


def send_forgot_password_otp(email, otp, system_settings, subject, request):
    try:
        logo = system_settings.website_logo if system_settings and system_settings.website_logo else ''
        logo_url = f"{settings.MEDIA_DOMAIN}{logo}" if logo else ''
        system_settings = system_settings
        static_url = f"{settings.STATIC_DOMAIN}"
        # Prepare context for email template
        context = {
            'otp': otp,
            'current_year': datetime.now().year,
            'logo': logo_url,
            'static_url': static_url,
        }
        email_content = render_to_string('emails/forgot_password_otp.html', context)
        
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
        # Log the error if needed
        print(f"Failed to send OTP email: {str(e)}")
        return False

############################ Reset Password OTP Verify API ############################
class ResetPasswordOtpVerifyAPI(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({
                'status': 0,
                'message': 'Email and OTP are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'User with this email does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        ##### For Testing Purpose
        if otp not in ['1234', 1234]:
            return Response({
                'status': 0,
                'message': 'Invalid OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)
        

        # # Check if OTP matches and is not expired (assuming 5 minutes validity)
        # if user.otp != otp or timezone.now() > user.otp_created_at + timedelta(minutes=5):
        #     return Response({
        #         'status': 0,
        #         'message': 'Invalid or expired OTP.'
        #     }, status=status.HTTP_400_BAD_REQUEST)

        # OTP is valid, proceed to reset password
        return Response({
            'status': 1,
            'message': 'OTP verified successfully. You can now reset your password.',
            'data': {
                'user_id': user.id
            }
        }, status=status.HTTP_200_OK)

############################ Reset Password API ############################
class ResetPasswordAPI(APIView):

    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not email or not otp or not new_password:
            return Response({
                'status': 0,
                'message': 'Email, OTP, and new password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'User with this email does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        # Check if OTP matches and is not expired (assuming 5 minutes validity)
        if user.otp != otp or timezone.now() > user.otp_created_at + timedelta(minutes=5):
            return Response({
                'status': 0,
                'message': 'Invalid or expired OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)
        # Validate the new password
        if len(new_password) < 8:
            return Response({
                'status': 0,
                'message': 'New password must be at least 8 characters long.'
            }, status=status.HTTP_400_BAD_REQUEST)
        # Set the new password and clear the OTP
        user.set_password(new_password)
        user.otp = None
        user.otp_created_at = None
        user.save()

        return Response({
            'status': 1,
            'message': 'Password reset successfully.'
        }, status=status.HTTP_200_OK)

######################### Dashboard API ############################
class DashboardAPI(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
                    
            
            # Only count notifications for authenticated users
            notification_count = 0
            if user.is_authenticated:
                notification_count = Notification.objects.filter(is_read=False, user=user).count()
            
            return Response({
                'status': 1,
                'message': 'Dashboard data retrieved successfully.',
                'data': {
                    'notification_count': notification_count
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while retrieving dashboard data.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


######################### Notification API ############################
class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    pagination_class = CustomPagination  # Added pagination

    # Get All Notifications
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            notifications_qs = user.notifications.all().order_by('-created_at')

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(notifications_qs, request)

            # Handle error case from paginator
            if isinstance(paginated_data, Response):
                return paginated_data

            serializer = NotificationSerializer(paginated_data, many=True)

            # Mark only the paginated ones as read
            notifications_qs.filter(id__in=[n.id for n in paginated_data]).update(is_read=True)

            # Return paginated response
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while retrieving notifications.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #Delete Single Notification
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            notification_id = request.data.get('notification_id')
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.delete()

            return Response({
                'status': 1,
                'message': 'Notification deleted successfully.'
            }, status=status.HTTP_200_OK)
            
        except Notification.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'Notification not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while deleting the notification.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    #Delete All Notification 
    def patch(self, request, *args, **kwargs):
        try:
            user = request.user
            notifications = user.notifications.all()
            notifications.delete()

            return Response({
                'status': 1,
                'message': 'All notifications deleted successfully.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while deleting notifications.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#################################### FAQ API View ####################################
class FAQListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = FAQ.objects.all().order_by('question')
    serializer_class = FAQSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        # Get all FAQs
        faqs = self.get_queryset()
        serializer = self.get_serializer(faqs, many=True)

        # Prepare the response with FAQs directly under 'data'
        return Response({
            'status': 1,
            'message': 'FAQ retrieved successfully.',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

##################### Profile Edit View API #####################
class EditProfileAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = UserSerializer(user, context={'request': request})
                        
            return Response({
                'status': 1,
                'message': 'Profile retrieved successfully.',
                'data': {
                    **serializer.data  # Merge serializer data directly
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while retrieving profile.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            data = request.data

            # Extract and validate fields
            name = data.get('name', '').strip()
            phone = data.get('phone', '').strip()
            dob_raw = data.get('date_of_birth', '').strip()
            anniversary_date_raw = data.get('anniversary_date', '').strip()
            address = data.get('address', '').strip()
            state = data.get('state', '').strip()
            city = data.get('city', '').strip()
            pincode = data.get('pincode', '').strip()

            if not name:
                return Response({
                    'status': 0,
                    'message': 'Name is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not phone:
                return Response({
                    'status': 0,
                    'message': 'Phone is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not dob_raw:
                return Response({
                    'status': 0,
                    'message': 'Date of birth is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse date of birth
            date_of_birth = parse_date(dob_raw)

            if not date_of_birth:
                return Response({
                    'status': 0,
                    'message': 'Invalid date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not phone.isdigit() or len(phone) != 10:
                return Response({
                    'status': 0,
                    'message': 'Phone number must be 10 digits.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if anniversary_date_raw:
                anniversary_date = parse_date(anniversary_date_raw)
                if not anniversary_date:
                    return Response({
                        'status': 0,
                        'message': 'Invalid anniversary date format. Use YYYY-MM-DD.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            state_obj = None
            if state:
                try:
                    state_obj = State.objects.get(id=state)
                except State.DoesNotExist:
                    return Response({
                        'status': 0,
                        'message': 'Invalid state.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            city_obj = None
            if city:
                try:
                    city_obj = City.objects.get(id=city)
                    # Clear existing cities and add the new one
                    user.cities.clear()
                    user.cities.add(city_obj)
                except City.DoesNotExist:
                    return Response({
                        'status': 0,
                        'message': 'Invalid city.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if pincode:
                if not pincode.isdigit() or len(pincode) != 6:
                    return Response({
                        'status': 0,
                        'message': 'Pincode must be 6 digits.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update user fields
            user.name = name
            name_parts = name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.phone = phone
            user.date_of_birth = date_of_birth
            user.anniversary_date = anniversary_date if anniversary_date_raw else None
            user.address = address
            user.state = state_obj if state else None
            user.pincode = pincode
            user.save()

            serializer = UserSerializer(user, context={'request': request})
            return Response({
                'status': 1,
                'message': 'Profile updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while updating profile.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


##################### Profile Picture Update View API #####################
class UpdateProfilePictureAPIView(APIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)    
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Ensure profile picture is in the request
        if "profile_picture" not in request.FILES:
            return Response({
                'status': 2,
                'message': 'No profile picture provided.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_profile_picture = user.profile_picture
        
        # Handle profile picture update
        if "profile_picture" in request.FILES:
            profile_picture = request.FILES["profile_picture"]
            if old_profile_picture and os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(old_profile_picture))):
                os.remove(os.path.join(settings.MEDIA_ROOT, str(old_profile_picture)))

            file_extension = profile_picture.name.split('.')[-1]
            unique_suffix = get_random_string(8)
            file_name = f"profile_pics/{user.id}_{unique_suffix}.{file_extension}"
            path = default_storage.save(file_name, profile_picture)
            user.profile_picture = path
        elif request.data.get("profile_picture") in [None, '']:  # Retain old picture if None/blank
            user.profile_picture = old_profile_picture
        # Save user details
        user.save()
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            'status': 1,
            'message': 'Profile Picture updated successfully.',
            'data': {
                **serializer.data  # Merge serializer data directly
            }
        }, status=status.HTTP_200_OK)

############################## Change Password API For User After Login ##############################
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):

        # Extract user from the request
        user = request.user
        
        # Get old and new passwords from request data
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        # Check if the old password is correct
        if not user.check_password(old_password):
            return Response({
                'status': 0,
                'message': 'Old password is incorrect.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate the new password
        if len(new_password) < 8:  # You can set your own validation logic
            return Response({
                'status': 0,
                'message': 'New password must be at least 8 characters long.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password and save the user
        user.set_password(new_password)
        user.save()

        return Response({
            'status': 1,
            'message': 'Password changed successfully. Please log in again.',
        }, status=status.HTTP_200_OK)

########### Delete User Account ##############
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()  # Permanently delete the user from the database

        return Response({
            'status': 1,
            'message': 'User account deleted successfully.',
        }, status=status.HTTP_200_OK)