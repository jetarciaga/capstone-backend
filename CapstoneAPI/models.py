from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import time, date, timedelta, datetime
from django.core.exceptions import ValidationError
from django.http import JsonResponse


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must set is_staff to True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must set is_superuser to True"))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email"), unique=True)
    firstname = models.CharField(max_length=50, blank=True)
    lastname = models.CharField(max_length=50, blank=True)
    birthday = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class BarangayDocument(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    requirements = models.ManyToManyField(
        "Requirement", related_name="barangay_documents", blank=True
    )

    def __str__(self):
        return self.name


class Requirement(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    """Schedule Object."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("ongoing", "Ongoing"),
        ("cancelled", "Cancelled"),
        ("done", "Done"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    purpose = models.ForeignKey(BarangayDocument, on_delete=models.CASCADE)
    timeslot = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    status_history = models.JSONField(default=list)
    reference_no = models.CharField(max_length=12, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "timeslot"], name="unique_schedule")
        ]
        ordering = ["-date", "timeslot"]

    def clean(self):
        if self.date <= date.today():
            raise ValidationError("The date must be tomorrow or later.")

        start_time = time(9, 0)
        end_time = time(15, 30)

        if not (start_time <= self.timeslot <= end_time):
            raise ValidationError(f"Time must be between {start_time} and {end_time}")

        if self.timeslot.minute % 30 != 0 or self.timeslot.second != 0:
            raise ValidationError("Time must be in 30-minute intervals.")

    def __str__(self):
        return f"{self.purpose} [{self.user.email}]"


class Email(models.Model):
    type = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type}: {self.subject}"
