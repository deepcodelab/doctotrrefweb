from user.models import DoctorProfile

def get_doctor_specialization(doctor_id):
    """Return specialization of the selected doctor."""
    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
        return doctor, doctor.specialization
    except DoctorProfile.DoesNotExist:
        return None, None

def get_similar_doctors(specialization, exclude_id):
    """Return doctors with same specialization sorted by rating & experience."""
    return (
        DoctorProfile.objects
        .filter(specialization=specialization)
        .exclude(id=exclude_id)
        .order_by('-rating', '-experience_years')
    )