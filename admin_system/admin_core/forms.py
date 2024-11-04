# admin_core/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from core.models import CustomUser

User = get_user_model()

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff']


class UserGroupForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['groups']