from rest_framework import routers
from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()

router.register(r"appointments", AppointmentViewSet, basename="appointment")



urlpatterns = [
     path('', include(router.urls)),
]