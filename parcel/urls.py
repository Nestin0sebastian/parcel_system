from django.urls import path
from .views import CreateParcelView

urlpatterns = [
    path('parcel/create/', CreateParcelView.as_view(), name='create-parcel'),
]