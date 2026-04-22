from django.urls import path
from .views import (
    TrackParcelView,
    UpdateTrackingView
)

urlpatterns = [
    path('track/<str:tracking_id>/', TrackParcelView.as_view()),
    path('tracking/update/', UpdateTrackingView.as_view()),
]