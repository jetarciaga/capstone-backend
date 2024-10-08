from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import CustomUser, BarangayDocument, Requirement, Schedule
from datetime import date, time


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


class ScheduleSerializer(serializers.ModelSerializer):
    # purpose and document_id points to same thing.
    user = CustomUserSerializer(required=True)
    document_id = serializers.PrimaryKeyRelatedField(queryset=BarangayDocument.objects.all(), write_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'user', 'date', 'purpose', 'timeslot', 'status', 'document_id']

    def validate_date(self, value):
        if value <= date.today():
            raise serializers.ValidationError('The date must be tomorrow or later.')
        return value

    def validate_timeslot(self, value):
        start_time = time(9, 0)
        end_time = time(15, 30)

        if not (start_time <= value <= end_time):
            raise serializers.ValidationError(f'Time must be between {start_time} and {end_time}.')

        if value.minute % 30 != 0 or value.second != 0:
            raise serializers.ValidationError('Time must be in 30-minute intervals.')
        return value

    def validate(self, data):
        date = data.get('date')
        timeslot = data.get('timeslot')

        if Schedule.objects.filter(date=date, timeslot=timeslot).exists():
            raise serializers.ValidationError("A schedule already exists for this date and time.")

    def create(self, validated_data):
        document = validated_data.pop('document_id')
        schedule = Schedule.objects.create(document=document, **validated_data)
        return schedule