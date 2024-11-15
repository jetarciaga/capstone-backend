from django.urls import path
from .views import (UserList, BarangayDocumentAPIView, BarangayDocumentListView,
                    ScheduleView, AvailableTimeSlotView, BarangayRequirementsListView
                    )

app_name = "capstoneapi"

urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('timeslots/', AvailableTimeSlotView.as_view(), name='available-timeslots'),
    path('documents/', BarangayDocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', BarangayDocumentAPIView.as_view(), name='document'),
    path('appointments/', ScheduleView.as_view(), name='appointment'),
    path('requirements/<int:pk>/', BarangayRequirementsListView.as_view(), name='requirements'),
]