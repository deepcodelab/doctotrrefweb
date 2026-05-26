import httpx
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from user.models import DoctorProfile, DoctorAvailability, CustomUser, Specialization
from core.models import Appointment
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny


# CHATBOT_SERVICE_URL = "http://localhost:8001/api/v1/respond"
CHATBOT_SERVICE_URL = "https://doctorchatbot.onrender.com/api/v1/respond"

class GlobalChatbotView(APIView):

    def post(self, request):
        user_message = request.data.get("message")
        history = request.data.get("history")

        if not user_message:
            return Response({"error": "Message is required"}, status=400)

        try:
            # Forward to microservice
            # with httpx.Client(timeout=120.0) as client:
            #     res = client.post(
            #         CHATBOT_SERVICE_URL,
            #         json={"message": user_message, "history":history}
            #     )
            # print(res,"vvvvv")

            auth_header = request.headers.get("Authorization")
            print(auth_header,"lljhh")

            with httpx.Client(timeout=120.0) as client:
                res = client.post(
                    CHATBOT_SERVICE_URL,
                    json={
                        "message": user_message,
                        "history": history
                    },
                    headers={
                        "Authorization": auth_header
                    }
                )


            return Response(res.json(), status=res.status_code)

        except httpx.RequestError:
            return Response(
                {"error": "Chatbot Service is unreachable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class SearchDoctors(APIView):
    
    def get(self,request):
        query = request.GET.get("q", "")

        doctors = DoctorProfile.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialization__name__icontains=query)
        ).select_related("user", "specialization")[:10]

        data = [
            {
                "id": d.id,
                "name": d.user.get_full_name(),
                "specialization": d.specialization.name if d.specialization else None,
                "experience": d.experience_years,
            }
            for d in doctors
        ]

        return JsonResponse(data, safe=False)



class DoctorAvailability(APIView):

    def generate_slots(self, start, end, minutes=30):
        slots = []
        current = datetime.combine(datetime.today(), start)
        end_dt = datetime.combine(datetime.today(), end)

        while current < end_dt:
            slots.append(current.time().strftime("%H:%M"))
            current += timedelta(minutes=minutes)

        return slots

    def get(self, request, doctor_id):
        date = request.GET.get("date")
        if not date:
            return JsonResponse({"error": "date parameter is required"}, status=400)

        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")

        avail = Availability.objects.filter(doctor_id=doctor_id, day=weekday).first()

        if not avail:
            return JsonResponse({"doctor_id": doctor_id, "slots": []})

        slots = self.generate_slots(avail.start_time, avail.end_time, minutes=30)

        return JsonResponse({
            "doctor_id": doctor_id,
            "date": date,
            "slots": slots
        })



@method_decorator(csrf_exempt, name='dispatch')
class BookAppointment(APIView):

    def post(self, request):
        payload = json.loads(request.body.decode("utf-8"))

        doctor_id = payload.get("doctor_id")
        user_id = payload.get("user_id")
        date = payload.get("date")
        time = payload.get("time")

        if not all([doctor_id, user_id, date, time]):
            return JsonResponse({"error": "Missing fields"}, status=400)

        doctor = DoctorProfile.objects.get(id=doctor_id)
        user = CustomUser.objects.get(id=user_id)

        # prevent double booking
        if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
            return JsonResponse({"error": "Slot already booked"}, status=400)

        appt = Appointment.objects.create(
            doctor=doctor,
            user=user,
            date=date,
            time=time,
        )

        return JsonResponse({
            "appointment_id": appt.id,
            "doctor": doctor.user.get_full_name(),
            "date": date,
            "time": time,
            "status": "booked"
        })


class SearchDoctorsAPI(APIView):

    def get(self, request):
        print("--------------------------------------------------------")
        specialty = request.GET.get("specialty")
        city = request.GET.get("city")
        # Validation
        if not specialty:
            return JsonResponse({"error": ("specialty is required")},status=400)

        if not city:
            return JsonResponse({"error": ("city is required")},status=400)

        doctors = (DoctorProfile.objects.filter(specialization__name__iexact=specialty,city__iexact=city).select_related("user","specialization")[:10])
        data = []

        for d in doctors:
            data.append({
                "id": d.id,
                "name": d.user.name or d.user.email,
                "specialty": d.specialization.name,
                "experience": d.experience_years,
                "certificate": d.certifications,
                "clinic_name": d.clinic_name,
                "address": d.clinic_address,
                "language": d.languages_spoken,
            })
        

        return JsonResponse(
            {
                "count": len(data),
                "doctors": data
            }
        )


class SpecializationAPIView(APIView):
    def get(self, request):
        spec = Specialization.objects.all()
        data = []
        for s in spec:
            data.append(
                {
            "name": s.name
        }
            )

        return JsonResponse(
            {
                "count" : len(data),
                "specialization":  data
            }
        )