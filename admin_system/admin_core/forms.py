# admin_core/forms.py

from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from core.models import CustomUser
from .models import CustomChart

User = get_user_model()

class UserEditForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff', 'groups']


class UserGroupForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['groups']

class ChartCreateForm(forms.ModelForm):
    model = forms.ChoiceField(choices=[(model.__name__, model._meta.verbose_name) for model in apps.get_models()], required=True)
    field = forms.ChoiceField(choices=[], required=True)

    class Meta:
        model = CustomChart
        fields = ['name', 'chart_type', 'data_source', 'model', 'field']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].choices = []  # Initialement vide, à remplir via AJAX