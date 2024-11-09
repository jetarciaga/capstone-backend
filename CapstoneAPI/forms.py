from django import forms
from .models import BarangayDocument, Requirement


class BarangayDocumentForm(forms.ModelForm):
    class Meta:
        model = BarangayDocument
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requirements'].queryset = Requirement.objects.filter()