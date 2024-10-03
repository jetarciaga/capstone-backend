from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated


User = get_user_model()


class UserList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)