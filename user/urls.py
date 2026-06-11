from rest_framework import routers
from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()

router.register(r"doctors", UserViewSet, basename="doctors_list")
router.register(r"user-register", UserRegister, basename="login_user")
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'availability', DoctorAvailibilityViewSet, basename="doctor_avaibilitty")
# router.register(r'chat_doctor_availability', DoctorAvailibilityViewSet, basename="chat_doctor_availability")


urlpatterns = [
     path('', include(router.urls)),
     path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
     path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
     path("recommend/from-doctor/<int:id>/", DoctorRecomandedAPIView.as_view()),
     path("chat_doctor_availability/<int:doctor_id>/", DoctorAvailabilityChatbotViewSet.as_view()),
]