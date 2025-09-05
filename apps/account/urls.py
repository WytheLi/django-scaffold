from django.urls import path

from . import views

urlpatterns = [
    path("sendCode/", views.VerificationCodeView.as_view(), name="send_code"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("verificationCode/login/", views.VerificationCodeLoginView.as_view(), name="verification_code_login"),
    path("profile/", views.AccountProfileView.as_view(), name="profile"),
]
