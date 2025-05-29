"""
URL configuration for lms_portal project.

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
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

from . import views

def root_redirect(request):
    return redirect('home')

urlpatterns = [
    path('', root_redirect),  # Redirect root URL to home
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('welcome/', views.welcome, name='welcome'),
    path('books/', views.book_collection, name='books'),
    path('about/', views.about, name='about'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/add_user/', views.add_user, name='add_user'),
    path('admin/add_book/', views.add_book, name='add_book'),
    path('books/checkout/', views.checkout_book, name='checkout'),
    path('api/current-borrowings/<int:member_id>/', views.get_current_borrowings, name='current_borrowings'),
    path('api/borrowing-history/<int:member_id>/', views.get_borrowing_history, name='borrowing_history'),
    path('api/pending-charges/<int:member_id>/', views.get_pending_charges, name='pending_charges'),
    path('api/book-history/<int:book_id>/', views.book_history, name='book_history'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_book/', views.add_book, name='add_book'),
    path('edit_book/', views.edit_book, name='edit_book'),
    path('delete_book/', views.delete_book, name='delete_book'),
    path('add_user/', views.add_user, name='add_user'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('delete_user/', views.delete_user, name='delete_user'),
]
