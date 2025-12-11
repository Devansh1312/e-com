from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("reward_admin.urls")),
    path('', include("reward_api.urls")),
]