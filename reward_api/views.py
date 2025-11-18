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
from django.db.models import Sum, Q, Prefetch
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.files.storage import default_storage
from django.core.paginator import EmptyPage
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_date
from django.utils.text import slugify
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

# ========================================
# Application-Specific Imports
# ========================================
from reward_admin.models import *
from reward_api.serializers import *


OTP_EXPIRY_MINUTES = 10


def _get_customer_role():
    preferred_names = ['Customer', 'Member', 'User']
    for name in preferred_names:
        role = Role.objects.filter(name__iexact=name).first()
        if role:
            return role
    return Role.objects.order_by('id').first()


def _generate_unique_username(seed_value: str) -> str:
    base_value = slugify(seed_value) if seed_value else ''
    if not base_value:
        base_value = f"user{random.randint(1000, 9999)}"
    username = base_value
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_value}{counter}"
        counter += 1
    return username


def _get_otp_timestamp(otp_instance):
    return otp_instance.updated_at or otp_instance.created_at


def _build_absolute_media_url(request, path):
    if not path:
        return None
    if request:
        return request.build_absolute_uri(path)
    return path


def _serialize_image(img, request=None):
    if not img or not img.image:
        return None
    url = _build_absolute_media_url(request, img.image.url)
    if not url:
        return None
    return {
        'id': img.id,
        'url': url,
        'is_primary': getattr(img, 'is_primary', False),
        'variant_id': img.variant_id,
    }


def serialize_product_record(product_obj, request=None):
    if not product_obj:
        return None

    prefetched_images = getattr(product_obj, 'prefetched_images', None)
    if prefetched_images is None:
        prefetched_images = list(product_obj.images.all())

    common_images = []
    for img in prefetched_images:
        if img.variant_id:
            continue
        serialized = _serialize_image(img, request)
        if serialized:
            common_images.append(serialized)

    variants_data = []
    available_sizes = {}
    available_colors = {}

    for variant in product_obj.variants.all():
        variant_images = []
        for img in variant.images.all():
            serialized = _serialize_image(img, request)
            if serialized:
                variant_images.append(serialized)

        size_payload = None
        if variant.size:
            size_payload = {'id': variant.size.id, 'name': variant.size.name}
            available_sizes[variant.size.id] = size_payload

        color_payload = None
        if variant.color:
            color_payload = {
                'id': variant.color.id,
                'name': variant.color.name,
                'hex_code': variant.color.hex_code
            }
            available_colors[variant.color.id] = color_payload

        variants_data.append({
            'id': variant.id,
            'size': size_payload,
            'color': color_payload,
            'stock_quantity': variant.stock_quantity,
            'sku': variant.sku,
            'status': variant.status,
            'images': variant_images,
        })

    # Determine featured image
    featured_image = None
    for variant in variants_data:
        primary = next((img for img in variant['images'] if img['is_primary']), None)
        if primary:
            featured_image = primary['url']
            break
        if variant['images'] and not featured_image:
            featured_image = variant['images'][0]['url']
    if not featured_image and common_images:
        featured_image = common_images[0]['url']

    return {
        'id': product_obj.id,
        'name': product_obj.name,
        'description': product_obj.description,
        'mrp': str(product_obj.MRP) if product_obj.MRP is not None else None,
        'sale_price': str(product_obj.sale_price) if product_obj.sale_price is not None else None,
        'status': product_obj.status,
        'url': product_obj.url,
        'category': {
            'id': product_obj.category.id,
            'name': product_obj.category.name,
        } if product_obj.category else None,
        'common_images': common_images,
        'variants': variants_data,
        'available_sizes': list(available_sizes.values()),
        'available_colors': list(available_colors.values()),
        'featured_image': featured_image,
        'created_at': product_obj.created_at.isoformat() if product_obj.created_at else None,
        'updated_at': product_obj.updated_at.isoformat() if product_obj.updated_at else None,
    }


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
        email = (request.data.get('email') or '').strip().lower()
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

        # Generate 4-digit OTP and persist (overwrite previous attempts)
        otp = random.randint(1000, 9999)
        otp_record, _ = OTPSave.objects.update_or_create(
            email=email,
            defaults={'OTP': otp}
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
                return Response({
                    'status': 0,
                    'message': 'Failed to send OTP email.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                'status': 1,
                'message': 'OTP sent successfully.',
                'data': {
                    'email': email,  
                    'otp': otp_record.OTP  
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Delete the OTP record if email fails to send
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
            'otp': str(otp),
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

    def post(self, request, *args, **kwargs):
        full_name = (request.data.get('name') or '').strip()
        email = (request.data.get('email') or '').strip().lower()
        phone = (request.data.get('phone') or '').strip()
        date_of_birth = (request.data.get('date_of_birth') or '').strip()
        password = request.data.get('password')
        otp = (request.data.get('otp') or '').strip()
        username_input = (request.data.get('username') or '').strip()

        if not all([full_name, email, phone, password, otp]):
            return Response({
                'status': 0,
                'message': 'Name, email, phone, password and OTP are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        if date_of_birth:
            parsed_dob = parse_date(date_of_birth)
            if not parsed_dob:
                return Response({
                    'status': 0,
                    'message': 'Invalid date format. Use YYYY-MM-DD.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            parsed_dob = None

        if len(password) < 8:
            return Response({
                'status': 0,
                'message': 'Password must be at least 8 characters long.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({
                'status': 0,
                'message': 'Email already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone=phone).exists():
            return Response({
                'status': 0,
                'message': 'Mobile number already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_record = OTPSave.objects.get(email=email)
        except OTPSave.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'Please request a new OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if str(otp_record.OTP) != otp:
            return Response({
                'status': 0,
                'message': 'Invalid OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        otp_timestamp = _get_otp_timestamp(otp_record)
        if otp_timestamp and timezone.now() > otp_timestamp + timedelta(minutes=OTP_EXPIRY_MINUTES):
            return Response({
                'status': 0,
                'message': 'OTP has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)

        username_seed = username_input or (email.split('@')[0] if email else phone)
        username = _generate_unique_username(username_seed)
        customer_role = _get_customer_role()

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                name=full_name,
                phone=phone,
                date_of_birth=parsed_dob,
                register_type='Mobile App',
                role=customer_role,
                is_active=True,
            )

            otp_record.delete()

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
            identifier = (
                request.data.get('identifier')
                or request.data.get('email')
                or request.data.get('username')
                or request.data.get('phone')
                or ''
            ).strip()
            password = request.data.get('password')

            if not identifier or not password:
                return Response({
                    'status': 0,
                    'message': 'Username/Email/Phone and password are required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            user = None
            if '@' in identifier:
                user = User.objects.filter(email__iexact=identifier).first()
            if user is None and identifier.isdigit():
                user = User.objects.filter(phone=identifier).first()
            if user is None:
                user = User.objects.filter(username__iexact=identifier).first()

            if user is None or not user.check_password(password):
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
            otp = random.randint(1000, 9999)
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
                    'data': {}
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
            'otp': str(otp),
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
        
        if user.otp is None or str(user.otp) != otp:
            return Response({
                'status': 0,
                'message': 'Invalid OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.otp_created_at or timezone.now() > user.otp_created_at + timedelta(minutes=OTP_EXPIRY_MINUTES):
            return Response({
                'status': 0,
                'message': 'OTP has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)

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
        if user.otp is None or str(user.otp) != otp:
            return Response({
                'status': 0,
                'message': 'Invalid OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)
        if not user.otp_created_at or timezone.now() > user.otp_created_at + timedelta(minutes=OTP_EXPIRY_MINUTES):
            return Response({
                'status': 0,
                'message': 'OTP has expired.'
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
            user = request.user if request.user.is_authenticated else None

            categories_qs = product_category.objects.filter(status=True).order_by('name')
            latest_products_qs = (
                product.objects.filter(status=True)
                .prefetch_related('images', 'category')
                .order_by('-created_at')[:10]
            )

            categories_data = [
                {
                    'id': category.id,
                    'name': category.name,
                    'status': category.status,
                }
                for category in categories_qs
            ]

            latest_products_data = [
                serialize_product_record(prod, request) for prod in latest_products_qs
            ]

            response_data = {
                'categories': categories_data,
                'latest_products': latest_products_data,
            }

            if user:
                response_data['user'] = UserSerializer(user, context={'request': request}).data
                response_data['cart_items'] = cart.objects.filter(customer=user).count()
                response_data['wishlist_items'] = wishlist.objects.filter(customer=user).count()

            return Response({
                'status': 1,
                'message': 'Dashboard data retrieved successfully.',
                'data': response_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while retrieving dashboard data.',
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

            name = data.get('name', '').strip()
            phone = data.get('phone', '').strip()
            dob_raw = data.get('date_of_birth', '').strip()
            address = data.get('address', '').strip()
            state_id = data.get('state')
            city_id = data.get('city')
            pincode = data.get('pincode', '').strip()
            gender_id = data.get('gender')
            country_id = data.get('country')

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

            if dob_raw:
                date_of_birth = parse_date(dob_raw)
                if not date_of_birth:
                    return Response({
                        'status': 0,
                        'message': 'Invalid date format. Use YYYY-MM-DD.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                date_of_birth = None

            if phone and (not phone.isdigit() or len(phone) != 10):
                return Response({
                    'status': 0,
                    'message': 'Phone number must be 10 digits.'
                }, status=status.HTTP_400_BAD_REQUEST)

            state_obj = None
            if state_id:
                try:
                    state_obj = State.objects.get(id=state_id)
                except State.DoesNotExist:
                    return Response({
                        'status': 0,
                        'message': 'Invalid state.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            city_obj = None
            if city_id:
                try:
                    city_obj = City.objects.get(id=city_id)
                except City.DoesNotExist:
                    return Response({
                        'status': 0,
                        'message': 'Invalid city.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            gender_obj = None
            if gender_id:
                try:
                    gender_obj = UserGender.objects.get(id=gender_id)
                except UserGender.DoesNotExist:
                    return Response({
                        'status': 0,
                        'message': 'Invalid gender.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            country_obj = None
            if country_id:
                try:
                    country_obj = Country.objects.get(id=country_id)
                except Country.DoesNotExist:
                    return Response({
                        'status': 0,
                        'message': 'Invalid country.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            if pincode:
                if not pincode.isdigit() or len(pincode) != 6:
                    return Response({
                        'status': 0,
                        'message': 'Pincode must be 6 digits.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.pincode = pincode

            user.name = name
            name_parts = name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.phone = phone
            user.date_of_birth = date_of_birth
            user.address = address
            user.state = state_obj if state_id else user.state
            user.gender = gender_obj if gender_id else user.gender
            user.country = country_obj if country_id else user.country

            if city_obj:
                user.cities.set([city_obj])
            elif city_id == '':
                user.cities.clear()
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

        if not old_password or not new_password:
            return Response({
                'status': 0,
                'message': 'Old and new passwords are required.',
            }, status=status.HTTP_400_BAD_REQUEST)

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

        if old_password == new_password:
            return Response({
                'status': 0,
                'message': 'New password must be different from the old password.',
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




#################################### Product Category Wise API View ####################################
class ProductCategoryWiseAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            category_id = request.query_params.get('category_id')
            if not category_id:
                return Response({
                    'status': 0,
                    'message': 'Category ID is required.',
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                category = product_category.objects.get(id=category_id, status=True)
            except product_category.DoesNotExist:
                return Response({
                    'status': 0,
                    'message': 'Category not found.',
                }, status=status.HTTP_404_NOT_FOUND)

            images_prefetch = Prefetch('images', queryset=product_image.objects.all(), to_attr='prefetched_images')
            variant_prefetch = Prefetch(
                'variants',
                queryset=product_variant.objects.select_related('size', 'color').prefetch_related('images')
            )

            products = (
                product.objects.filter(category=category, status=True)
                .select_related('category')
                .prefetch_related(images_prefetch, variant_prefetch)
                .order_by('-created_at')
            )

            product_data = [serialize_product_record(prod, request) for prod in products]

            return Response({
                'status': 1,
                'message': 'Product category wise data retrieved successfully.',
                'data': {
                    'category': {
                        'id': category.id,
                        'name': category.name,
                    },
                    'products': product_data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while retrieving product category wise data.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


################# product list with All Images API View ####################################
class ProductListWithImagesAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            category_id = request.query_params.get('category_id')
            search = request.query_params.get('search')

            products_qs = product.objects.filter(status=True)
            if category_id:
                products_qs = products_qs.filter(category_id=category_id)
            if search:
                products_qs = products_qs.filter(name__icontains=search)

            images_prefetch = Prefetch('images', queryset=product_image.objects.all(), to_attr='prefetched_images')
            variant_prefetch = Prefetch(
                'variants',
                queryset=product_variant.objects.select_related('size', 'color').prefetch_related('images')
            )

            products_qs = (
                products_qs
                .select_related('category')
                .prefetch_related(images_prefetch, variant_prefetch)
                .order_by('-created_at')
            )

            products_data = [serialize_product_record(prod, request) for prod in products_qs]

            return Response({
                'status': 1,
                'message': 'Products retrieved successfully.',
                'data': products_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while retrieving products.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductDetailAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get(self, request, pk, *args, **kwargs):
        try:
            images_prefetch = Prefetch('images', queryset=product_image.objects.all(), to_attr='prefetched_images')
            variant_prefetch = Prefetch(
                'variants',
                queryset=product_variant.objects.select_related('size', 'color').prefetch_related('images')
            )
            product_obj = (
                product.objects.select_related('category')
                .prefetch_related(images_prefetch, variant_prefetch)
                .get(id=pk, status=True)
            )
            data = serialize_product_record(product_obj, request)
            return Response({
                'status': 1,
                'message': 'Product retrieved successfully.',
                'data': data
            }, status=status.HTTP_200_OK)
        except product.DoesNotExist:
            return Response({
                'status': 0,
                'message': 'Product not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 0,
                'message': 'An error occurred while retrieving product detail.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response({
                    'status': 0,
                    'message': 'Authentication required to add items to cart.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            product_id = request.data.get('product_id')
            if not product_id:
                return Response({
                    'status': 0,
                    'message': 'Product ID is required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                product_obj = product.objects.get(id=product_id, status=True)
            except product.DoesNotExist:
                return Response({
                    'status': 0,
                    'message': 'Product not found.'
                }, status=status.HTTP_404_NOT_FOUND)

            cart_item, created = cart.objects.get_or_create(
                customer=request.user,
                product=product_obj
            )

            message = 'Product added to cart.' if created else 'Product already in cart.'
            total_items = cart.objects.filter(customer=request.user).count()

            return Response({
                'status': 1,
                'message': message,
                'data': {
                    'cart_item_id': cart_item.id,
                    'total_items': total_items
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'Unable to add product to cart.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            images_prefetch = Prefetch('product__images', queryset=product_image.objects.all())
            variant_prefetch = Prefetch(
                'product__variants',
                queryset=product_variant.objects.select_related('size', 'color').prefetch_related('images')
            )
            cart_items = (
                cart.objects.filter(customer=request.user)
                .select_related('product__category')
                .prefetch_related(images_prefetch, variant_prefetch)
                .order_by('-created_at')
            )

            items_data = []
            total_amount = Decimal('0.00')
            for item in cart_items:
                product_obj = item.product
                if not product_obj:
                    continue
                product_data = serialize_product_record(product_obj, request)
                price = product_obj.sale_price
                if price is None:
                    price = product_obj.MRP
                if price is None:
                    price = Decimal('0.00')
                total_amount += price
                items_data.append({
                    'cart_item_id': item.id,
                    'product': product_data,
                    'price': str(price)
                })

            return Response({
                'status': 1,
                'message': 'Cart data retrieved successfully.',
                'data': {
                    'items': items_data,
                    'total_items': len(items_data),
                    'total_amount': str(total_amount)
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'Unable to fetch cart data.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddToWishlistAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            product_id = request.data.get('product_id')
            if not product_id:
                return Response({
                    'status': 0,
                    'message': 'Product ID is required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                product_obj = product.objects.get(id=product_id, status=True)
            except product.DoesNotExist:
                return Response({
                    'status': 0,
                    'message': 'Product not found.'
                }, status=status.HTTP_404_NOT_FOUND)

            wishlist_item, created = wishlist.objects.get_or_create(
                customer=request.user,
                product=product_obj
            )

            message = 'Product added to wishlist.' if created else 'Product already in wishlist.'
            total_items = wishlist.objects.filter(customer=request.user).count()

            return Response({
                'status': 1,
                'message': message,
                'data': {
                    'wishlist_item_id': wishlist_item.id,
                    'total_items': total_items
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'Unable to add product to wishlist.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WishlistListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            images_prefetch = Prefetch('product__images', queryset=product_image.objects.all())
            variant_prefetch = Prefetch(
                'product__variants',
                queryset=product_variant.objects.select_related('size', 'color').prefetch_related('images')
            )
            wishlist_items = (
                wishlist.objects.filter(customer=request.user)
                .select_related('product__category')
                .prefetch_related(images_prefetch, variant_prefetch)
                .order_by('-created_at')
            )

            items_data = []
            for item in wishlist_items:
                product_obj = item.product
                if not product_obj:
                    continue
                product_data = serialize_product_record(product_obj, request)
                items_data.append({
                    'wishlist_item_id': item.id,
                    'product': product_data,
                })

            return Response({
                'status': 1,
                'message': 'Wishlist data retrieved successfully.',
                'data': {
                    'items': items_data,
                    'total_items': len(items_data),
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 0,
                'message': 'Unable to fetch wishlist data.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
