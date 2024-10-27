from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import requests
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.shortcuts import get_object_or_404
from accounts.tokens import account_activation_token
from .models import CustomUser
from .serializers import CustomUserSerializer, LogoutSerializer, ResendActivationEmailSerializer, \
    PasswordResetSerializer, PasswordChangeSerializer, AuthSerializer, VerifyOTPSerializer, ResendOTPSerializer, \
    GoogleLoginSerializer, AccessTokenSerializer, UpdateUserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)


class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'OTP verified'}, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResendOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'New OTP sent'}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token


class UserInfoFromTokenAPI(APIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = AccessTokenSerializer
    def get(self, request):
        # If authenticated, get the user from the request
        user = request.user
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "hint": user.hints,
            "transcribe_text": user.transcribed,
            "dp": user.profile_picture.url if user.profile_picture else None,
        }
        return Response(user_data, status=status.HTTP_200_OK)


    # def post(self, request):
    #     # Initialize the serializer with the request data
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # Extract the access token from the validated data
    #     access_token = serializer.validated_data['access_token']
    #
    #     try:
    #         # Decode the token and retrieve the user
    #         token = AccessToken(access_token)
    #         user_id = token['user_id']
    #         user = User.objects.get(id=user_id)
    #
    #         # Prepare the user data to return
    #         user_data = {
    #             "first_name": user.first_name,
    #             "last_name": user.last_name,
    #             "email": user.email,
    #         }
    #
    #         return Response(user_data, status=status.HTTP_200_OK)
    #
    #     except (TokenError, InvalidToken, User.DoesNotExist):
    #         return Response({"error": "Invalid token or user not found."}, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserInfoAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer  # Reference the serializer class here

    def patch(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data,
                                           partial=True)  # Instantiate the serializer with data

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class UserList(generics.ListAPIView):
    queryset = User.objects.all().order_by('pk')
    serializer_class = CustomUserSerializer
    page_size = 1


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'password reset email sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            password = request.data.get('password')
            password_confirm = request.data.get('password_confirm')

            if password and password_confirm and password == password_confirm:
                user.set_password(password)
                user.save()
                return Response({'status': 'password reset complete'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'reset link is invalid'}, status=status.HTTP_400_BAD_REQUEST)


# ================================================Social Authentication================================================
# Function to get Google user info
def get_google_user_info(access_token):
    print("Hello")
    import requests
    response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("This is response:", response)
    return response.json()


class GoogleAuthAPI(APIView):
    serializer_class = GoogleLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        print("Hello")
        access_token = request.data.get("access_token")
        print(access_token)
        user_info = get_google_user_info(access_token)
        print("User info:", user_info)
        email = user_info.get("email")
        if not user_info or not user_info.get("email"):
            return {"Error": "Authentication failed"}

        # Get or create the user
        user, created = User.objects.get_or_create(email=email)
        if created or not user.is_email_verified:
            user.first_name = user_info.get("name")
            user.profile_picture = user_info.get("picture")
            user.is_email_verified = True
            user.save()
        # Create JWT token
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response({"user": user.id, "token": token}, status=status.HTTP_200_OK)
