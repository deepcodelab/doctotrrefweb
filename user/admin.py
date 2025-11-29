from django.contrib import admin
from .models import CustomUser, DoctorProfile, CustomerProfile, Specialization, DoctorAvailability


# Register your models here.


class UserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ["name", "email", "role"]
    search_fields = ["name", "email", "role"]


admin.site.register(CustomUser, UserAdmin)
admin.site.register(DoctorProfile)
admin.site.register(CustomerProfile)
admin.site.register(Specialization)
admin.site.register(DoctorAvailability)