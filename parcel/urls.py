from django.urls import path
from .views import CreateParcelView, CalculatePriceView

urlpatterns = [
    path('parcel/create/', CreateParcelView.as_view(), name='create-parcel'),
    path('parcel/calculate-price/', CalculatePriceView.as_view(), name='calculate-price'),
]