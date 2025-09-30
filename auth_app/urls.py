from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('refresh', views.refresh_token_view, name='refresh'),
    path('forgot-password', views.forgot_password_view, name='forgot-password'),
    path('reset-password', views.reset_password_view, name='reset-password'),
    path('profile', views.user_profile_view, name='profile'),
]
