from django.db import models
from django.contrib.auth import get_user_model
from core.models import VersionedModel
from django.conf import settings


class ProjectSetting(VersionedModel):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.key} : {self.value}"


User = get_user_model()


class CustomChart(VersionedModel):
    name = models.CharField(max_length=255)
    chart_type = models.CharField(max_length=50, choices=[
        ('pie', 'Pie'),
        ('bar', 'Bar'),
        ('line', 'Line'),
        # Ajouter d'autres types de graphiques
    ])
    data_source = models.TextField(help_text="Chemin ou nom de la source des données")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Setting(models.Model):
    key = models.CharField(max_length=255)
    value = models.TextField()

    @staticmethod
    def get_visible_fields(model_name):
        setting = Setting.objects.filter(key=f'{model_name}_visible_fields').first()
        return setting.value.split(',') if setting and setting.value else []

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=50, choices=[("INFO", "Info"), ("ERROR", "Error")])
    message = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_core_log_entries'
    )

    def __str__(self):
        return f"[{self.timestamp}] {self.level}: {self.message}"