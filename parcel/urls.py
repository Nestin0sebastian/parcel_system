from django.urls import path
from .views import (
    CreateParcelView,
    CheckoutView,
    ConfirmParcelView,
    InvoiceView,
    CancelParcelView,
    PickupRequestListView,     
    AcceptPickupView,
    MyPickupParcelsView,
    StaffDashboardView,
    UserParcelListView,        
    UserParcelDetailView,
    HubParcelListView,
    DeliveryRequestListView,
    AcceptDeliveryView,
    MyDeliveryParcelsView,
    
)

urlpatterns = [
    # 🔹 USER FLOW
    path("create/", CreateParcelView.as_view()),
    path('checkout/<int:parcel_id>/', CheckoutView.as_view()),
    path('confirm/<int:parcel_id>/', ConfirmParcelView.as_view()),
    path("invoice/<str:tracking_id>/", InvoiceView.as_view()),
    path('cancel/<int:parcel_id>/', CancelParcelView.as_view()),

    # 🔥 NEW USER DASHBOARD
    path("my-parcels/", UserParcelListView.as_view()),                     # ✅ NEW
    path("my-parcels/<int:parcel_id>/", UserParcelDetailView.as_view()),   # ✅ NEW

    # 🔹 STAFF DASHBOARD
    path("staff/dashboard/", StaffDashboardView.as_view()),
    path("hub/parcels/", HubParcelListView.as_view()),

    # 🔹 PICKUP FLOW
    path("pickup/requests/", PickupRequestListView.as_view()),
    path("pickup/accept/<int:parcel_id>/", AcceptPickupView.as_view()),
    path("pickup/my-parcels/", MyPickupParcelsView.as_view()),

    path("delivery/requests/", DeliveryRequestListView.as_view()),
    path("delivery/accept/<int:parcel_id>/", AcceptDeliveryView.as_view()),
    path("delivery/my-parcels/", MyDeliveryParcelsView.as_view()),
]