from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import path, re_path
from django.views.static import serve
from .views import *

urlpatterns = [
    # Redirect root to admin login
    path('', lambda request: redirect('adminlogin')),


    # -------- Authentication --------
    path('adminlogin/', LoginFormView, name="adminlogin"),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', ForgotPasswordAdminView.as_view(), name='Forgot_Password_Admin'),
    path('verify-otp-admin/', VerifyOTPAdminView.as_view(), name='verify_otp_admin'),
    path('reset-password-admin/', ResetPasswordAdminView.as_view(), name='reset_password_admin'),

    # -------- Dashboards --------
    path('Dashboard/', Dashboard.as_view(), name="view_dashboard"),


    # -------- Profile --------
    path('System-Settings/', System_Settings.as_view(), name="System_Settings"),
    path('user_profile/', UserProfileView.as_view(), name='user_profile'),
    path('edit_profile/', UserUpdateProfileView.as_view(), name='edit_profile'),
    path('change_password_ajax/', change_password_ajax, name='change_password_ajax'),

    # -------- Location APIs --------
    path('api-get-states/', api_get_states, name='get_states'),
    path('api-get-cities/', api_get_cities, name='get_cities'),
    path('get-states/', get_states, name='get_states'),
    path('get-cities/', get_cities, name='get_cities'),

   
    # -------- User Roles --------
    path('user-roles/', RoleView.as_view(), name='role_list'),
    # path('user-role/create/', RoleCreateView.as_view(), name='role_create'),
    path('user-role/edit/<int:role_id>/', RoleEditView.as_view(), name='role_edit'),
    # path('user-role/delete/<int:role_id>/', RoleDeleteView.as_view(), name='role_delete'),


    # -------- Club Members --------
    path('club-member/', ClubMemberList.as_view(), name='club_member_list'),
   
    path('club-members/edit/<int:pk>/', ClubMemberEditView.as_view(), name='club_member_edit'),
    path('club-members/toggle-status/<int:pk>/', ClubMemberToggleStatusView.as_view(), name='club_member_toggle_status'),
    path('club-members/delete/<int:pk>/', ClubMemberDeleteView.as_view(), name='club_member_delete'),

    # -------- Sub-Admins --------
    path('sub-admin/', SubAdminList.as_view(), name='sub_admin_list'),
    path('sub-admin/create/', SubAdminCreateView.as_view(), name='sub_admin_create'),
    path('sub-admin/edit/<int:pk>/', SubAdminEditView.as_view(), name='sub_admin_edit'),
    path('sub-admin/detail/<int:pk>/', SubAdminDetailView.as_view(), name='sub_admin_detail'),
    path('sub-admin/toggle-status/<int:pk>/', SubAdminToggleStatusView.as_view(), name='sub_admin_toggle_status'),
    path('sub-admin/delete/<int:pk>/', SubAdminDeleteView.as_view(), name='sub_admin_delete'),

    # -------- FAQ --------
    path('faq/', FAQView.as_view(), name='faq_list'),
    path('faq/create/', FAQCreateView.as_view(), name='faq_create'),
    path('faq/edit/<int:faq_id>/', FAQEditView.as_view(), name='faq_edit'),
    path('faq/delete/<int:faq_id>/', FAQDeleteView.as_view(), name='faq_delete'),

    # -------- Country/State/City --------
    path('countries/', CountryListView.as_view(), name='country_list'),
    path('countries/create/', CountryCreateView.as_view(), name='country_create'),
    path('countries/edit/<int:pk>/', CountryEditView.as_view(), name='country_edit'),
    path('countries/delete/<int:pk>/', CountryDeleteView.as_view(), name='country_delete'),
    path('states/', StateListView.as_view(), name='state_list'),
    path('states/create/', StateCreateView.as_view(), name='state_create'),
    path('states/edit/<int:pk>/', StateEditView.as_view(), name='state_edit'),
    path('states/delete/<int:pk>/', StateDeleteView.as_view(), name='state_delete'),
    path('cities/', CityListView.as_view(), name='city_list'),
    path('cities/create/', CityCreateView.as_view(), name='city_create'),
    path('cities/edit/<int:pk>/', CityEditView.as_view(), name='city_edit'),
    path('cities/delete/<int:pk>/', CityDeleteView.as_view(), name='city_delete'),
]

# ================================
# Static & Media Serving
# ================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
