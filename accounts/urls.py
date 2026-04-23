from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [

    # 🔐 AUTH
    path('auth/signup/', SignupView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/logout/', LogoutView.as_view()),

    # 👨‍💼 ADMIN
    path('admin/create-staff/', CreateStaffView.as_view()),
    path('admin/delete-staff/<int:staff_id>/', DeleteStaffView.as_view()),
    path('admin/staff/', StaffListView.as_view()),
    path('admin/users/', UserListView.as_view()),
    path('admin/user/<int:user_id>/', UserDetailView.as_view()),
    path('admin/parcels/', ParcelListView.as_view()),
    path('admin/dashboard/', AdminDashboardView.as_view()),

    # 📦 PARCEL DETAIL (ADD THIS)
    path('parcel/<int:parcel_id>/', ParcelDetailView.as_view()),
    path('staff/accept-delivery/<int:parcel_id>/', AcceptDeliveryView.as_view()),
    path('staff/deliver/<int:parcel_id>/', DeliverParcelView.as_view()),
    path('staff/generate-otp/<int:parcel_id>/', GenerateOTPView.as_view()),
]