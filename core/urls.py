from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import settings
from faqs.views import FAQViewSet  # Ensure this import is correct

# Define a router for API endpoints
router = DefaultRouter()
router.register(r'faqs', FAQViewSet, basename='faq')

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('api/', include(router.urls)),
    path('ckeditor5/', include('django_ckeditor_5.urls')),  # API routes
]   
