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
