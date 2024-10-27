from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, CustomTokenObtainPairView, LogoutView, UserDetail, UserList, LogoutAllView, \
    PasswordResetView, PasswordResetConfirmView, VerifyOTPView, ResendOTPView, GoogleAuthAPI, UserInfoFromTokenAPI, \
    UpdateUserInfoAPI

app_name = 'accounts'

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('api/resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/user-info/', UserInfoFromTokenAPI.as_view(), name='user-info-from-token'),
    path('api/user/update/', UpdateUserInfoAPI.as_view(), name='user-update'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
    path('api/users/', UserList.as_view()),
    path('api/users/<int:pk>/', UserDetail.as_view()),
    path('api/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/password-reset-confirm/<slug:uidb64>/<slug:token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('api/google/', GoogleAuthAPI.as_view(), name="google_authenticaiton"),
]
