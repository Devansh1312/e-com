from django.urls import path
from reward_api.views import *

urlpatterns = [
    # -------------------- Authentication --------------------
    path('api/send-otp/', SendRegistrationOTP.as_view()),  # Send OTP for registration
    path('api/verify-otp/', VerifyOTPAndRegister.as_view()),  # Verify OTP & register user
    path('api/login/', LoginAPI.as_view()),  # User login
    path('api/logout/', LogoutAPI.as_view()),  # User logout

    # -------------------- Password Management --------------------
    path('api/forgot-password/', ForgotPasswordAPI.as_view()),  # Request password reset
    path('api/reset-password-otp-verify/', ResetPasswordOtpVerifyAPI.as_view()),  # Verify OTP for password reset
    path('api/reset-password/', ResetPasswordAPI.as_view()),  # Reset password

    # -------------------- Dashboard --------------------
    path('api/dashboard/', DashboardAPI.as_view()),  # User dashboard data

    # -------------------- Product Catalog --------------------
    path('api/product-category/', ProductCategoryWiseAPIView.as_view()),
    path('api/products/', ProductListWithImagesAPIView.as_view()),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view()),

    # -------------------- Cart & Wishlist --------------------
    path('api/cart/', CartListAPIView.as_view()),
    path('api/cart/add/', AddToCartAPIView.as_view()),
    path('api/wishlist/', WishlistListAPIView.as_view()),
    path('api/wishlist/add/', AddToWishlistAPIView.as_view()),

    # -------------------- FAQs --------------------
    path('api/faq/', FAQListAPIView.as_view()),  # List FAQs

    # -------------------- Profile Management --------------------
    path('api/user/profile/', EditProfileAPI.as_view()),  # View/update user profile
    path('api/update-profile-img/', UpdateProfilePictureAPIView.as_view()),  # Update profile picture
    path('api/change-password/', ChangePasswordAPIView.as_view()),  # Change password
    path('api/delete_account/', DeleteUserView.as_view()),  # Delete account
]
