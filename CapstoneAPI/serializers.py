from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import CustomUser, BarangayDocument, Requirement


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'password')


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email')


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = ('id', 'name')


class BarangayDocumentSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, required=False)
    requirement_ids = serializers.PrimaryKeyRelatedField(queryset=Requirement.objects.all(), many=True, write_only=True)

    class Meta:
        model = BarangayDocument
        fields = ['id', 'name', 'description', 'requirements', 'requirement_ids']

    def create(self, validated_data):
        requirements = validated_data.pop('requirement_ids')
        document = BarangayDocument.objects.create(**validated_data)
        document.requirements.set(requirements)
        return document