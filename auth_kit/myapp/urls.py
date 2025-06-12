"""
URL configurations for the myapp module.

This module defines the URL patterns and their corresponding views
for the myapp API endpoints. It maps URL paths to view functions or classes
that handle HTTP requests.
"""

from django.urls import path

from auth_kit.myapp.views import MyView

urlpatterns = [
    # Define URL pattern for the MyView API view
    path("get/", MyView.as_view(), name="myapp"),
]
