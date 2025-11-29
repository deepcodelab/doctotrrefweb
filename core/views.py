from django.shortcuts import render
from .models import Appointment
from user.models import *
from .serializers import AppointmentSerializer, HomePageSerializer, DoctorHomePageSerializer
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # If the user is a doctor → show appointments for them
        # if hasattr(user, "doctor_profile"):
        if user.role == "doctor":
            print("bbbbb")
            return Appointment.objects.filter(doctor__user=user).order_by("-created_at")

        # If the user is a customer → show their own appointments
        # elif hasattr(user, "customer_profile"):
        elif user.role == 'customer':
            print("hhhhhkkk")
            return Appointment.objects.filter(customer__user=user).order_by("-created_at")

        return Appointment.objects.none()

    def list(self, request, *args, **kwargs):
        print("llllll")
        queryset = self.get_queryset()
        print(queryset,"hhhh")
        serializer = self.serializer_class(queryset, many=True, context={"request": request})

        return Response({
            "success": True,
            "data": serializer.data
        })



    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # 👈 add this line
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def perform_create(self, serializer):
        serializer.save()

    
    def partial_update(self, request, *args, **kwargs):
        appointment = self.get_object()
        print("jjjjfjfjjffjjjffjfj")
        new_status = request.data.get("status")

        if new_status not in ["pending", "confirmed", "completed", "cancelled"]:
            return Response(
                {"error": "Invalid status value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🩺 Allow only doctor or customer involved in the appointment
        user = request.user
        if user.role == "doctor" and appointment.doctor.user != user:
            return Response({"error": "You are not authorized to modify this appointment."}, status=status.HTTP_403_FORBIDDEN)
        if user.role == "customer" and appointment.customer.user != user:
            return Response({"error": "You are not authorized to modify this appointment."}, status=status.HTTP_403_FORBIDDEN)

        appointment.status = new_status
        appointment.save()

        serializer = self.get_serializer(appointment)
        return Response({
            "success": True,
            "message": f"Appointment status updated to {new_status}.",
            "data": serializer.data
        })


class HomePageViewSet(APIView):
    def get(self, request, *args, **kwargs):
        print(request.user,'llllll')
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        customer = CustomerProfile.objects.filter(user=request.user).first()
        appointments = Appointment.objects.filter(customer=customer, appointment_date__gte=timezone.now())
        serializer = HomePageSerializer(appointments, context={"request": request}, many=True)
        print(serializer.data,'llll')
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        

class DoctorHomePageViewSet(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        print(user,';llll')
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        doctor = DoctorProfile.objects.filter(user=user).first()
        serializer = DoctorHomePageSerializer(doctor, context={"request": request})
        print(serializer.data,'llll')
        return Response(serializer.data, status=status.HTTP_200_OK)
