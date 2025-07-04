from django.contrib.auth.models import User
from rest_framework import serializers
from django.urls import reverse
from django.core.mail import send_mail
import re

# Jeśli masz własny model UserProfile, zaimportuj go:
# from .models import UserProfile

# Jeśli korzystasz z custom user model:
from django.contrib.auth import get_user_model
User = get_user_model()

#user_register
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    # password standards
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain an uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain a lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain a digit.")
        if not re.search(r'[^\w\s]', value):
            raise serializers.ValidationError("Password must contain a special character.")
        return value

    # user creation with activation link
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            is_active=False
        )
        # Upewnij się, że masz account_activation_token zaimportowany!
        from .tokens import account_activation_token
        uid = serializers.IntegerField().to_representation(user.pk)
        activation_link = self.context['request'].build_absolute_uri(
            reverse('activate-account', kwargs={'uid': uid, 'token': account_activation_token.make_token(user)})
        )
        subject = 'Activate your account'
        message = (
            f'Hi {user.username},\n\n'
            f'Click the link below to activate your account:\n'
            f'{activation_link}\n\n'
            'If this wasn’t you, please ignore this message.'
        )

        send_mail(subject, message, None, [user.email])
        return user

# resend activation link
class ResendActivationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is registered with this email address.")

        if user.is_active:
            raise serializers.ValidationError("This account is already activated.")

        self.user = user
        return value

    def save(self):
        user = self.user
        from .tokens import account_activation_token
        uid = serializers.IntegerField().to_representation(user.pk)
        request = self.context.get('request')

        activation_link = request.build_absolute_uri(
            reverse('activate-account', kwargs={'uid': uid, 'token': account_activation_token.make_token(user)})
        )

        subject = 'Activate your account'
        message = (
            f'Hi {user.username},\n\n'
            f'Click the link below to activate your account:\n'
            f'{activation_link}\n\n'
            'If this wasn’t you, please ignore this message.'
        )

        send_mail(subject, message, None, [user.email])

#user_login
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


# password_reset_request
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("User with this email does not exist or is not active.")
        return value

# password_reset_set
class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain an uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain a lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain a digit.")
        if not re.search(r'[^\w\s]', value):
            raise serializers.ValidationError("Password must contain a special character.")
        return value

    # validation if new password is the same as new password confirm
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        
        self.validate_password(attrs['new_password'])
        return attrs

    #saving new password
    def save(self):
        from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
        from django.utils.http import urlsafe_base64_decode
        from django.contrib.auth.tokens import PasswordResetTokenGenerator

        uid = self.validated_data['uidb64']
        token = self.validated_data['token']

        try:
            uid = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or uid.")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is expired or invalid.")

        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

# password serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain an uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain a lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain a digit.")
        if not re.search(r'[^\w\s]', value):
            raise serializers.ValidationError("Password must contain a special character.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validate password strength
        self.validate_password(attrs['new_password'])
        
        # Check if new password is different from old password
        user = self.context['request'].user
        if user.check_password(attrs['new_password']):
            raise serializers.ValidationError("New password cannot be the same as the old password.")
        
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

# --- Profile serializers ---

from rest_framework.validators import UniqueValidator

# Jeśli masz model UserProfile, odkomentuj poniższy import i użyj go w serializerze
# from .models import UserProfile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    # Jeśli Twój model User ma pole profile_picture, odkomentuj poniższą linię
    # profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        # Jeśli User nie ma pola profile_picture, usuń je z poniższej listy
        fields = ['username', 'email']  # Dodaj 'profile_picture' jeśli istnieje

# Jeśli masz model UserProfile z polem profile_picture, odkomentuj poniższy serializer
# class ProfilePictureSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ['profile_picture']

from .models import Mood, DayEntry, TodoItem, UserProfile

class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ['id', 'name', 'icon']

class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = ['id', 'user', 'day_entry', 'content', 'is_done']

class DayEntrySerializer(serializers.ModelSerializer):
    mood = MoodSerializer(read_only=True)
    mood_id = serializers.PrimaryKeyRelatedField(
        queryset=Mood.objects.all(), source='mood', write_only=True, required=False
    )
    todos = TodoItemSerializer(many=True, read_only=True)

    class Meta:
        model = DayEntry
        fields = ['id', 'user', 'date', 'mood', 'mood_id', 'description', 'todos']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'profile_picture']


# password_reset_request
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("User with this email does not exist or is not active.")
        return value


# password_reset_set
class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain an uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain a lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain a digit.")
        if not re.search(r'[^\w\s]', value):
            raise serializers.ValidationError("Password must contain a special character.")
        return value

    # validation if new password is the same as new password confirm
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        
        self.validate_password(attrs['new_password'])
        return attrs

    #saving new password
    def save(self):
        uid = self.validated_data['uidb64']
        token = self.validated_data['token']

        try:
            uid = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or uid.")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is expired or invalid.")

        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

# password serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain an uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain a lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain a digit.")
        if not re.search(r'[^\w\s]', value):
            raise serializers.ValidationError("Password must contain a special character.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validate password strength
        self.validate_password(attrs['new_password'])
        
        # Check if new password is different from old password
        user = self.context['request'].user
        if user.check_password(attrs['new_password']):
            raise serializers.ValidationError("New password cannot be the same as the old password.")
        
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    