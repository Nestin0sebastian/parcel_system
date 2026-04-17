from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('parcel.urls')),
    path('api/', include('tracking.urls')),
]