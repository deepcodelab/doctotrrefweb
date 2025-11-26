from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers import *
from .models import CustomUser, DoctorProfile, CustomerProfile, DoctorAvailability
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from main.ml.doc_recomanded import get_doctor_specialization, get_similar_doctors

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

class UserRegister(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializers
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        data = request.data
        print(data,"jdgsfs")
        serializer = self.serializer_class(data=data)
        print
        if serializer.is_valid():
            user = serializer.save()
            return Response ({
                "success": True,
                "data": serializer.data
            })
        else:
            print("fdjdfjdfh", serializer.errors)
            return Response ({
                "success": False,
                "data": serializer.errors
            })


# class UserViewSet(ModelViewSet):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializers
#     permission_classes = [IsAuthenticated]


#     def list(self, request, *args, **kwargs):
#         print("llllllllllll")
#         user_list = CustomUser.objects.filter(role="doctor")
#         print("user list", user_list)

#         serializer = self.serializer_class(user_list, many=True)
#         return Response({
#             "success": True,
#             "data": serializer.data
#         })

#     def retrieve(self, request, *args, **kwargs):
#         user = self.get_object()
#         # user = CustomUser.objects.filter(id = user_id).first()

#         serializer = self.serializer_class(user)

#         return Response({
#             "success": True,
#             "data": serializer.data
#         })



class UserViewSet(ModelViewSet):
    queryset = DoctorProfile.objects.select_related("user").all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        print("Fetching all doctors...")
        doctors = self.queryset
        serializer = self.serializer_class(doctors, many=True, context={"request": request})
        print(serializer.data)
        return Response({
            "success": True,
            "data": serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        doctor = self.get_object()
        serializer = self.serializer_class(doctor)
        return Response({
            "success": True,
            "data": serializer.data
        })


# class DoctorProfileViewSet(ModelViewSet):
#     queryset = DoctorProfile.objects.all()
#     serializer_class = DoctorProfileSerializer
#     permission_classes = [IsAuthenticated]


class CustomerProfileViewSet(ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]


# class ProfileViewSet(ModelViewSet):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializers
#     permission_classes = [IsAuthenticated]

#     @action(detail=False, methods=['get'], url_path='me')
#     def get_my_profile(self, request):
#         print("jdjdjdjdjdjdjdjdj")
#         user = request.user
#         print(user,"lhjjhj")
#         user_data = UserSerializers(user).data

#         # Doctor Profile
#         if user.role == "doctor":
#             profile = DoctorProfile.objects.filter(user=user).first()
#             profile_data = DoctorProfileSerializer(profile).data if profile else None
#             return Response({
#                 "role": user.role,
#                 "user": user_data,
#                 "profile": profile_data
#             })

#         # Customer Profile
#         elif user.role == "customer":
#             profile = CustomerProfile.objects.filter(user=user).first()
#             profile_data = CustomerProfileSerializer(profile).data if profile else None
#             return Response({
#                 "role": user.role,
#                 "user": user_data,
#                 "profile": profile_data
#             })

#         # Admin or no profile
#         return Response({
#             "role": user.role,
#             "user": user_data,
#             "profile": None,
#             "message": "Admin or unassigned profile"
#         })


class ProfileViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializers
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def get_my_profile(self, request):
        user = request.user

        # PATCH (update)
        if request.method == 'PATCH':
            if user.role == "doctor":
                profile = DoctorProfile.objects.filter(user=user).first()
                serializer = DoctorProfileSerializer(profile, data=request.data, partial=True)
            elif user.role == "customer":
                profile = CustomerProfile.objects.filter(user=user).first()
                serializer = CustomerProfileSerializer(profile, data=request.data, partial=True)
            else:
                return Response({"detail": "Admin cannot update profile."}, status=400)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # GET (fetch)
        user_data = UserSerializers(user).data
        if user.role == "doctor":
            profile = DoctorProfile.objects.filter(user=user).first()
            profile_data = DoctorProfileSerializer(profile).data if profile else None
        elif user.role == "customer":
            profile = CustomerProfile.objects.filter(user=user).first()
            profile_data = CustomerProfileSerializer(profile).data if profile else None
        else:
            profile_data = None

        return Response({
            "role": user.role,
            "user": user_data,
            "profile": profile_data
        })


class DoctorAvailibilityViewSet(ModelViewSet):
    queryset = DoctorAvailability.objects.all()
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            availability = serializer.save()  # 👈 automatically adds doctor (handled in serializer)
            return Response({
                "message": "Slot added successfully",
                "data": DoctorAvailabilitySerializer(availability).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Something went wrong",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DoctorRecomandedAPIView(APIView):

    def get(self, request, id):
        print(id,"lllll")
        doctor, specialization = get_doctor_specialization(id)

        if not doctor:
            return Response(
                {"error": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        similar = get_similar_doctors(specialization, doctor.id)

        return Response({
            "recommended": DoctorProfileSerializer(similar, many=True).data
        })