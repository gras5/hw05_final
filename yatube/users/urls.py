from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        views.UserPasswordChange.as_view(),
        name='password_change_form'
    ),
    path(
        'password_change/done/',
        views.UserPasswordChangeDone.as_view(),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        views.UserPasswordReset.as_view(),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        views.UserPasswordResetDone.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        views.UserPasswordResetConfirm.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        views.UserPasswordResetComplete.as_view(),
        name='password_reset_complete'
    ),
]
