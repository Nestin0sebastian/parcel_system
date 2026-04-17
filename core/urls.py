from django.urls import path
from .views import (
    SignupView,
    LoginView,
    CreateParcelView,
    TrackParcelView,
    UpdateTrackingView
)

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),

    path('parcel/create/', CreateParcelView.as_view()),
    path('parcel/track/<str:tracking_id>/', TrackParcelView.as_view()),
    path('tracking/update/', UpdateTrackingView.as_view()),
]