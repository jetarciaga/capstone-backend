from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.filters import OrderingFilter
from .serializers import CustomUserSerializer, BarangayDocumentSerializer, ScheduleSerializer, AvailableTimeSlotSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import BarangayDocument, Schedule
from django.shortcuts import get_object_or_404
from datetime import datetime


User = get_user_model()


class UserList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            users = get_object_or_404(User, pk=pk)
            serializer = CustomUserSerializer(users)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # if request.user.is_staff:
        #     users = User.objects.all()
        #     serializer = CustomUserSerializer(users, many=True)
        else:
            users = request.user
            serializer = CustomUserSerializer(users)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BarangayDocumentAPIView(APIView):
    def get(self, request, pk):
        document = get_object_or_404(BarangayDocument, pk=pk)
        serializer = BarangayDocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BarangayRequirementsListView(APIView):
    def get(self, request, pk):
        document = get_object_or_404(BarangayDocument, id=pk)
        serializer = BarangayDocumentSerializer(document)

        data = serializer.data["requirements"]
        return Response(data, status=status.HTTP_200_OK)


class BarangayDocumentListView(APIView):
    def get(self, request):
        document = BarangayDocument.objects.all()
        serializer = BarangayDocumentSerializer(document, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_staff:
            return Response({'detail': 'User not allowed, this will be reported.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BarangayDocumentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleView(GenericAPIView):
    serializer_class = ScheduleSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['date', 'timeslot', 'status']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Schedule.objects.all()
        else:
            return Schedule.objects.filter(user=self.request.user)

    def get(self, request, pk=None):
        if pk:
            schedule = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = self.get_serializer(schedule)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            return Response({"message": "Created Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):

        if not pk:
            return Response({"error": "Appointment id is required for updating status"}, status=status.HTTP_400_BAD_REQUEST)

        schedule = get_object_or_404(self.get_queryset(), pk=pk)
        new_status = request.data.get("status")

        if not new_status:
            return Response({"error": "Status field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in dict(Schedule.STATUS_CHOICES).keys():
            return Response({"error": f"Invalid status value. Allowed values are {', '.join(dict(Schedule.STATUS_CHOICES).keys())}"}, status=status.HTTP_400_BAD_REQUEST)

        if schedule.status != new_status:
            schedule.status_history.append({
                "status": schedule.status,
                "timestamp": datetime.now().isoformat()
            })

            schedule.status = new_status
            schedule.save()

        serializer = self.get_serializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AvailableTimeSlotView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AvailableTimeSlotSerializer(data=request.data)

        if serializer.is_valid():
            available_slots = serializer.get_available_slots()

            if not available_slots:
                return Response({"available_slots": []}, status=status.HTTP_200_OK)
            return Response({"available_slots": available_slots}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
