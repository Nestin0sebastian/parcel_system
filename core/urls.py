from django.urls import path
from .views import ApplyJobView, SignupView, LoginView

urlpatterns = [
    path('apply/', ApplyJobView.as_view()),
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
]