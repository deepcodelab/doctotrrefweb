from rest_framework import serializers
from .models import Appointment
from user.models import DoctorProfile, CustomerProfile

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.user.name", read_only=True)
    customer_name = serializers.CharField(source="customer.user.name", read_only=True)
    image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor",
            "doctor_name",
            "customer",
            "customer_name",
            "appointment_date",
            "appointment_time",
            "notes",
            "status",
            "created_at",
            "image",
        ]
        read_only_fields = ["customer", "status", "created_at"]

    def get_image(self, obj):
        request = self.context["request"]
        if obj.doctor.profile_image:
            return request.build_absolute_uri(obj.doctor.profile_image.url)
        return None

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        # Ensure customer exists
        customer_profile = CustomerProfile.objects.filter(user=user).first()
        if not customer_profile:
            raise serializers.ValidationError("Customer profile not found.")

        # Ensure doctor exists
        doctor = validated_data.get("doctor")
        if not doctor:
            raise serializers.ValidationError("Doctor is required.")

        # Create appointment
        appointment = Appointment.objects.create(
            customer=customer_profile,
            **validated_data,
        )
        return appointment


class HomePageSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.user.name", read_only=True)
    specialty = serializers.CharField(source="doctor.specialty", read_only=True)
    image = serializers.SerializerMethodField()  
    location = serializers.CharField(source="doctor.clinic_address", read_only=True)

    appointment_date = serializers.DateField(format="%Y-%m-%d")
    appointment_time = serializers.TimeField(format="%H:%M")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor_name",
            "specialty",
            "appointment_date",
            "appointment_time",
            "status",
            "notes",
            "location",
            "image",
        ]


    def get_image(self, obj):
        request = self.context["request"]
        if obj.doctor.profile_image:
            return request.build_absolute_uri(obj.doctor.profile_image.url)
        return None

class DoctorAppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.user.name", read_only=True)
    appointment_date = serializers.DateField(format="%Y-%m-%d")
    appointment_time = serializers.TimeField(format="%H:%M")
    image = serializers.SerializerMethodField()
    doctor_image = serializers.SerializerMethodField() 


    class Meta:
        model = Appointment
        fields = [
            "id",
            "customer_name",
            "appointment_date",
            "appointment_time",
            "status",
            "notes",
            "image",
            "doctor_image"
        ]


    def get_image(self, obj):
        request = self.context["request"]
        if obj.customer.profile_picture:
            return request.build_absolute_uri(obj.customer.profile_picture.url)
        return None


    def get_doctor_image(self, obj):
        request = self.context["request"]
        if obj.doctor.profile_image:
            return request.build_absolute_uri(obj.doctor.profile_image.url)
        return None


class DoctorHomePageSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name", read_only=True)
    appointments = serializers.SerializerMethodField()
    doctor_image = serializers.SerializerMethodField()
    specialization = serializers.CharField(source="specialization.name")

    class Meta:
        model = DoctorProfile
        fields = ["id", "name", "appointments", "doctor_image", "specialization", 'clinic_name', 'clinic_address']

    def get_doctor_image(self, obj):
        request = self.context["request"]
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def get_appointments(self, obj):
        request = self.context["request"]
        appointments = Appointment.objects.filter(doctor=obj)
        if appointments:
            appointment_data=DoctorAppointmentSerializer(appointments, context={"request": request}, many=True)
            return appointment_data.data
        return None