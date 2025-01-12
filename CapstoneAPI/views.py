from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.filters import OrderingFilter
from .serializers import (
    CustomUserSerializer,
    BarangayDocumentSerializer,
    ScheduleSerializer,
    AvailableTimeSlotSerializer,
    EmailSerializer,
)

from string import Template
from types import SimpleNamespace
import json

from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import BarangayDocument, Schedule, Email
from django.shortcuts import get_object_or_404
from datetime import datetime

from django.http import JsonResponse
from CapstoneAPI.email_utils import send_email_with_ses


User = get_user_model()


class UserList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            users = get_object_or_404(User, pk=pk)
            serializer = CustomUserSerializer(users)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.query_params.get("all"):
            users = User.objects.all()
            serializer = CustomUserSerializer(users, many=True)
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
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not request.user.is_staff:
            return Response(
                {"detail": "User not allowed, this will be reported."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = BarangayDocumentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleView(GenericAPIView):
    serializer_class = ScheduleSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["date", "timeslot", "status"]
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

            filter_date = request.query_params.get("date", None)
            if filter_date:
                try:
                    date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
                    queryset = queryset.filter(date=date_obj)
                except ValueError:
                    return Response(
                        {"error": "Invalid date format. User YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # todo: add filter by reference number
            filter_reference_number = request.query_params.get("reference_number", None)
            if filter_reference_number:
                queryset = queryset.filter(
                    reference_no__icontains=filter_reference_number
                )

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            return Response(
                {"message": "Created Successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk=None):

        if not pk:
            return Response(
                {"error": "Appointment id is required for updating status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        schedule = get_object_or_404(self.get_queryset(), pk=pk)
        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {"error": "Status field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_status not in dict(Schedule.STATUS_CHOICES).keys():
            return Response(
                {
                    "error": f"Invalid status value. Allowed values are {', '.join(dict(Schedule.STATUS_CHOICES).keys())}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if schedule.status != new_status:
            schedule.status_history.append(
                {"status": schedule.status, "timestamp": datetime.now().isoformat()}
            )

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
            return Response(
                {"available_slots": available_slots}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailView(APIView):
    def get(self, request, type):
        email = get_object_or_404(Email, type=type)
        serializer = EmailSerializer(email)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        email = self.get(request, kwargs["type"])
        email = self.generate_email(request.data, email.data)
        response = send_email_with_ses(
            email.subject, email.message, request.data["recipient"]
        )
        if response:
            return JsonResponse(
                {"message": "Email sent successfully", "response": response},
                status=status.HTTP_200_OK,
            )
        return JsonResponse(
            {"message": "Failed to send email"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @staticmethod
    def extract_requirements(requirements):
        data = []
        for i, requirement in enumerate(requirements, 1):
            data.append(f"\t{i}. {requirement["name"]}")
        return "\n".join(data)

    def generate_email(self, request, email):
        details = SimpleNamespace(**request)
        email = SimpleNamespace(**email)
        document = get_object_or_404(BarangayDocument, id=details.document)
        print("CHECK", request)

        requirements = self.extract_requirements(details.requirements)
        message = Template(email.message).substitute(
            reference_number=details.reference_number,
            user=details.user,
            status=details.status,
            document=document,
            date=details.date,
            time=details.time,
            requirements=requirements,
        )
        email.message = message
        return email
