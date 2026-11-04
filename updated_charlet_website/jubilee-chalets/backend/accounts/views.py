import secrets
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User, PasswordResetToken
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    tokens = get_tokens_for_user(user)
    return Response({'user': UserSerializer(user).data, 'tokens': tokens}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def login_view(request):
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    tokens = get_tokens_for_user(user)
    return Response({'user': UserSerializer(user).data, 'tokens': tokens})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass
    return Response({'message': 'Logged out successfully.'})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    if request.method == 'GET':
        return Response(UserSerializer(user).data)

    serializer = UserSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    request.user.set_password(serializer.validated_data['new_password'])
    request.user.save()
    return Response({'message': 'Password changed successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def password_reset_request_view(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email'].lower()

    try:
        user = User.objects.get(email=email)
        token_str = secrets.token_urlsafe(32)
        PasswordResetToken.objects.create(user=user, token=token_str)

        reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={user.pk}&token={token_str}"
        send_mail(
            subject='Reset your Jubilee Chalets password',
            message=f'Click the link to reset your password: {reset_url}\n\nThis link expires in 2 hours.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except User.DoesNotExist:
        pass  # Prevent email enumeration

    return Response({'message': 'If an account with that email exists, a reset link has been sent.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.get(pk=serializer.validated_data['uid'])
        reset_token = PasswordResetToken.objects.get(
            user=user,
            token=serializer.validated_data['token'],
            is_used=False,
        )
    except (User.DoesNotExist, PasswordResetToken.DoesNotExist):
        return Response({'message': 'Invalid or expired reset link.'}, status=status.HTTP_400_BAD_REQUEST)

    if not reset_token.is_valid():
        return Response({'message': 'This reset link has expired.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(serializer.validated_data['new_password'])
    user.save()
    reset_token.is_used = True
    reset_token.save()

    return Response({'message': 'Password reset successfully.'})
