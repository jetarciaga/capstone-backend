from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomUserSerializer, BarangayDocumentSerializer
from rest_framework.permissions import IsAuthenticated
from .models import BarangayDocument
from django.shortcuts import get_object_or_404


User = get_user_model()


class UserList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BarangayDocumentAPIView(APIView):
    def get(self, request, pk):
        document = get_object_or_404(BarangayDocument, pk=pk)
        serializer = BarangayDocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BarangayDocumentListView(APIView):
    def get(self, request):
        document = BarangayDocument.objects.all()
        serializer = BarangayDocumentSerializer(document, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BarangayDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



