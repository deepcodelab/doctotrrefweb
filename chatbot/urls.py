from django.urls import path
from .views import *

urlpatterns = [
    path("chat/", GlobalChatbotView.as_view(), name="global-chatbot"),
    path("doctors/search/", SearchDoctors.as_view()),
    path("availability/<int:doctor_id>/", DoctorAvailability.as_view()),
    path("appointments/book/", BookAppointment.as_view()),

]