from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .serializers import RegisterSerializer, PasswordResetRequestSerializer, SetNewPasswordSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import UserRateThrottle

# user view
class RegisterAPI(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

# account activation
class ActivateAccount(APIView):
    permission_classes = []

    def get(self, request, uid, token):
        user = get_object_or_404(User, pk=uid)
        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'status': 'account activated'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
# resend activation email
class ResendActivationEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ResendActivationEmailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Activation link sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# throttling
class LoginRateThrottle(UserRateThrottle):
    scope = 'login'

class ThrottledTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

# password reset system
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = []  # AllowAny

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        user = User.objects.get(email=email, is_active=True)

        #token and UID
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
        frontend_reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{uidb64}/{token}/"

        #end mail
        subject = "Password reset"
        message = (
            f"Hi {user.username},\n\n"
            f"Click the link to reset your password:\n{frontend_reset_url}\n\n"
             "If this wasn’t you, please ignore this message."
        )
        send_mail(subject, message, None, [user.email], fail_silently=False)

        return Response({"status": "reset link sent"}, status=status.HTTP_200_OK)

class SetNewPasswordAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = []  # AllowAny

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"status": "password reset complete"}, status=status.HTTP_200_OK)

class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = {
            "username": user.username,
            "email": user.email,
            "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None,
        }
        return Response(data)

    def patch(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = {}
        if 'email' in request.data:
            user.email = request.data['email']
            user.save()
            data['email'] = user.email
        if 'username' in request.data:
            user.username = request.data['username']
            user.save()
            data['username'] = user.username
        # obsługa zdjęcia profilowego jak wcześniej
        serializer = ProfilePictureSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data['profile_picture'] = request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
        return Response(data)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"detail": "Account deleted."}, status=status.HTTP_204_NO_CONTENT)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

