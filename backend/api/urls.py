from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # logowanie
    path('api/register/', views.RegisterView.as_view(), name='register'),         # rejestracja
    path('api/password-reset-request/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    # Dodaj kolejne endpointy według potrzeb...
]