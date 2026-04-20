from django.urls import path
from .views import CreateParcelView, CheckoutView, ConfirmParcelView, InvoiceView

urlpatterns = [
    path("create/", CreateParcelView.as_view()),
    path("checkout/<str:tracking_id>/", CheckoutView.as_view()),
    path("confirm/<str:tracking_id>/", ConfirmParcelView.as_view()),
    path("invoice/<str:tracking_id>/", InvoiceView.as_view()),
]