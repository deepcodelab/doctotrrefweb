from django.db import models
from django.utils import timezone
from user.models import DoctorProfile, CustomerProfile

class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Appointment(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="appointments"
    )
    customer = models.ForeignKey(
        CustomerProfile, on_delete=models.CASCADE, related_name="appointments"
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.PENDING
    )
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.customer.user.name or self.customer.user.email} -> {self.doctor.user.name or self.doctor.user.email} on {self.appointment_date}"
