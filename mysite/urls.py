from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('spot/', include('spot.urls')),
    path('admin/', admin.site.urls),
]