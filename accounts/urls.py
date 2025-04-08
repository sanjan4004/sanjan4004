# accounts/urls.py
from django.urls import path
from .views import SignUpView, ProfileUpdateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from .views import register, user_login

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path("accounts/login/", auth_views.LoginView.as_view()),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout')
]
