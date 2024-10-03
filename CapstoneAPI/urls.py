from django.urls import path
from .views import UserList, BarangayDocumentAPIView, BarangayDocumentListView

urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('documents/', BarangayDocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', BarangayDocumentAPIView.as_view(), name='document'),
]