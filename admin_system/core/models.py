from datetime import datetime
import json
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class VersionHistory(models.Model):
    content_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    version = models.PositiveIntegerField()
    data = models.JSONField()
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'version')
        ordering = ['-modified_at']

    def __str__(self):
        return f"Version {self.version} of {self.content_type} (ID {self.object_id})"


class VersionedModel(models.Model):
    version = models.PositiveIntegerField(default=1)
    last_modified = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk:
            self.version += 1
            # Convertir les champs en un dictionnaire JSON-compatible
            VersionHistory.objects.create(
                content_type=self.__class__.__name__,
                object_id=self.pk,
                version=self.version,
                data=self.to_dict()  # Utilise la méthode to_dict pour garantir la compatibilité JSON
            )
        super().save(*args, **kwargs)

    def to_dict(self):
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, datetime):
                data[field.name] = value.isoformat()  # Convertir les objets datetime en ISO 8601
            elif hasattr(value, 'pk'):  # Pour les ForeignKey, OneToOneField, etc.
                data[field.name] = value.pk  # Stocker uniquement la clé primaire
            else:
                data[field.name] = value
        return data


class CustomUser(VersionedModel, AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_verified = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username


class UserProfile(VersionedModel, models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"