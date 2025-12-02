from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, DoctorProfile, CustomerProfile,DoctorAvailability, DoctorDateAvailability


# -------------------- JWT Token Serializer --------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }

        data = super().validate(credentials)
        user = self.user
        data.update({
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
            }
        })
        return data


# -------------------- User Serializer --------------------
class UserSerializers(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        role = validated_data.get("role")

        if role == "doctor":
            DoctorProfile.objects.create(user=user)
        elif role == "customer":
            CustomerProfile.objects.create(user=user)
        return user


# -------------------- Doctor Profile Serializer --------------------
# class DoctorProfileSerializer(ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     user_name = serializers.CharField(source='user.name', read_only=True)

#     class Meta:
#         model = DoctorProfile
#         fields = [
#             'id',
#             'user',
#             'user_email',
#             'user_name',
#             'specialization',
#             'description',
#         ]



class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDateAvailability
        fields = ['id','date', 'start_time', 'end_time']
        # read_only_fields =["doctor"]

    def create(self, validated_data):
        """
        Automatically attach the doctor from request context.
        """
        print(validated_data,"llll")
        request = self.context.get('request')
        doctor = None

        if request and hasattr(request, 'user'):
            print("kkkkkk")
            doctor = DoctorProfile.objects.filter(user=request.user).first()

        if not doctor:
            raise serializers.ValidationError("Doctor profile not found for this user.")

        # ✅ Attach doctor before saving
        validated_data['doctor'] = doctor
        print(validated_data, "lllll")  # for debugging

        return super().create(validated_data)


class DoctorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    date_availabilities = DoctorAvailabilitySerializer(many=True, read_only=True)
    specialization = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'specialization',
            'description',
            'experience_years',
            'clinic_name',
            'clinic_address',
            'consultation_fee',
            "image_url",
            'rating',
            'date_availabilities',
        ]

    def get_specialization(self, obj):
        if obj.specialization:
            doc = obj.specialization.name
            return doc
        return None

    def get_image_url(self, obj):
        request = self.context.get("request", None)

        # If no request, return relative URL safely
        # if not request:
        #     if obj.profile_image:
        #         print(";;;;;;;;", obj.profile_image.url)
        #         return obj.profile_image.url
        #     return None

        # If request exists, return absolute URL
        if obj.profile_image:
            print("kkkk", )
            return request.build_absolute_uri(obj.profile_image.url)

        return None

    def update(self, instance, validated_data):
        availabilities_data = validated_data.pop('availabilities', [])
        instance = super().update(instance, validated_data)

        # Update or create availabilities
        for availability in availabilities_data:
            DoctorDateAvailability.objects.update_or_create(
                doctor=instance,
                date=availability.get('date'),
                defaults={
                    'start_time': availability.get('start_time'),
                    'end_time': availability.get('end_time'),
                },
            )

        return instance



# -------------------- Customer Profile Serializer --------------------
class CustomerProfileSerializer(ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'age',
            'gender',
            'address',
            'medical_history',
            'blood_group',
            'emergency_contact',
            'profile_picture',
            # 'image_url',
        ]

    # def get_image_url(self, obj):
    #     req = self.context["request"]
    #     if req.user.role == "customer":
    #         if obj.profile_picture:
    #             return req.build_absolute_uri(obj.profile_picture.url)
    #         return None

    #     if req.user.role == "doctor":
    #         if obj.profile_image:
    #             return req.build_absolute_uri(obj.profile_image.url)
    #         return None
