from django.urls import path
from .views import CreateParcelView, CheckoutView, ConfirmParcelView, InvoiceView

urlpatterns = [
    path("create/", CreateParcelView.as_view()),
   path('checkout/<int:parcel_id>/', CheckoutView.as_view()),
   path('confirm/<int:parcel_id>/', ConfirmParcelView.as_view()),
    path("invoice/<str:tracking_id>/", InvoiceView.as_view()),
]