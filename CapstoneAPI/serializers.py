from djoser.serializers import UserCreateSerializer, UserSerializer, UserCreatePasswordRetypeSerializer
from rest_framework import serializers
from .models import CustomUser, BarangayDocument, Requirement, Schedule
from datetime import date, time, datetime, timedelta


class CustomUserCreateSerializer(UserCreateSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'firstname', 'lastname', 'birthday', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Password do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'firstname', 'lastname', 'birthday', 'is_staff')


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
    # user = CustomUserSerializer(required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=True)
    purpose = serializers.PrimaryKeyRelatedField(queryset=BarangayDocument.objects.all())
    purpose_name = serializers.SerializerMethodField()


    class Meta:
        model = Schedule
        fields = ['id', 'user', 'date', 'purpose', 'purpose_name', 'timeslot', 'status', "status_history"]

    def get_purpose_name(self, obj):
        if obj.purpose:
            return obj.purpose.name
        return None

    def update(self, instance, validated_data):
        """Handles updates to the schedule."""
        print("PATCH requests triggered")

        if "status" in validated_data:
            status = validated_data.get("status")
            mapping = {
                "pending": "ongoing",
                "ongoing": "done"
            }
            instance.status = mapping[status]

        for attr, value in validated_data.items():
            if attr != "status":
                setattr(instance, attr, value)
        # Save the instance; status_history is handled by the model's save() method
        instance.save()
        return instance

    def validate_date(self, value):
        if not self.instance:
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
        return data

    def create(self, validated_data):
        # document = validated_data.pop('document_id')
        # validated_data["purpose"] = document
        schedule = Schedule.objects.create(**validated_data)
        return schedule


class AvailableTimeSlotSerializer(serializers.Serializer):
    selected_date = serializers.DateField()

    def validate_selected_date(self, value):
        if value < datetime.now().date():
            raise serializers.ValidationError("The date cannot be in the past.")
        return value

    def get_available_slots(self):
        selected_date = self.validated_data["selected_date"]

        start_time = datetime.combine(selected_date, time(9,0))
        end_time = datetime.combine(selected_date, time(15, 30))
        interval = timedelta(minutes=30)
        all_slots = []

        while start_time <= end_time:
            all_slots.append(start_time.time())
            start_time += interval

        booked_slots = Schedule.objects.filter(date=selected_date).values_list("timeslot", flat=True)
        available_slots = [slot.strftime("%H:%M") for slot in all_slots if slot not in booked_slots]

        return available_slots

