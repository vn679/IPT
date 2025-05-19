"""


The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('blank-page/', views.blank_page, name='blank_page'),
    path('error-404/', views.error_404, name='error_404'),
    path('error-500/', views.error_500, name='error_500'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('basic-table/', views.basic_table, name='basic_table'),
    path('basic-elements/', views.basic_elements, name='basic_elements'),
    path('buttons/', views.buttons, name='buttons'),
    path('chartjs/', views.chartjs, name='chartjs'),
    path('dropdowns/', views.dropdowns, name='dropdowns'),
    path('font-awesome/', views.font_awesome, name='font_awesome'),
    path('typography/', views.typography, name='typography'),
    path('make-reservation/', views.make_reservation, name='make_reservation'),
    path('update-reservation-status/', views.update_reservation_status, name='update_reservation_status'),
    path('get-available-rooms/', views.get_available_rooms, name='get_available_rooms'),
    path('rooms/', views.rooms, name='rooms'),
    path('reports/', views.reports, name='reports'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
