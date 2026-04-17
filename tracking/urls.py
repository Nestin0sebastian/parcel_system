from django.urls import path
from .views import (
    TrackParcelView,
    UpdateTrackingView
)

urlpatterns = [
    path('parcel/track/<str:tracking_id>/', TrackParcelView.as_view()),
    path('tracking/update/', UpdateTrackingView.as_view()),
]