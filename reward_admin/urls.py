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

    # Customer URLs
    path('customer-users/', CustomerUserListView.as_view(), name='customer_user_list'),
    path('customer/detail/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customer/toggle-status/<int:pk>/', CustomerToggleStatusView.as_view(), name='customer_toggle_status'),



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

    # Product Category URLs
    path('product-categories/', ProductCategoryListView.as_view(), name='product_category_list'),
    path('product-categories/create/', ProductCategoryCreateView.as_view(), name='product_category_create'),
    path('product-categories/edit/<int:pk>/', ProductCategoryEditView.as_view(), name='product_category_edit'),
    path('product-categories/delete/<int:pk>/', ProductCategoryDeleteView.as_view(), name='product_category_delete'),

    # Product URLs
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/edit/<int:pk>/',ProductEditView.as_view(), name='product_edit'),
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),

    # Customer Review URLs
    path('customer-reviews/', CustomerReviewListView.as_view(), name='customer_review_list'),
    path('customer-reviews/view/<int:pk>/', CustomerReviewDetailView.as_view(), name='customer_review_view'),
    path('customer-reviews/edit/<int:pk>/', CustomerReviewEditView.as_view(), name='customer_review_edit'),
    path('customer-reviews/delete/<int:pk>/', CustomerReviewDeleteView.as_view(), name='customer_review_delete'),
    
    # Contact Us URLs
    path('contact-us/', ContactUsListView.as_view(), name='contact_us_list'),
    path('contact-us/view/<int:pk>/', ContactUsDetailView.as_view(), name='contact_us_view'),
    path('contact-us/edit/<int:pk>/', ContactUsEditView.as_view(), name='contact_us_edit'),
    path('contact-us/delete/<int:pk>/', ContactUsDeleteView.as_view(), name='contact_us_delete'),

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
