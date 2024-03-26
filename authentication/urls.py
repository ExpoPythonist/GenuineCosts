from .views import RegistrationView, UsernameValidationView, EmailValidationView, LogoutView, VerificationView, \
    LoginView, AccountView, AccountEditView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('user-info', AccountView.as_view(), name="account_view"),
    path('user-edit/<int:pk>', AccountEditView.as_view(), name="account_edit"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()),
         name="validate-username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()),
         name='validate_email'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
]
