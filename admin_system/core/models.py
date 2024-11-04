from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class VersionHistory(models.Model):
    content_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    version = models.PositiveIntegerField()
    data = models.JSONField()
    modified_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

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

            # Vérifiez si la version existe déjà dans `VersionHistory`
            exists = VersionHistory.objects.filter(
                content_type=self.__class__.__name__,
                object_id=self.pk,
                version=self.version
            ).exists()

            # Incrémentez la version jusqu'à ce qu'elle soit unique
            while exists:
                self.version += 1
                exists = VersionHistory.objects.filter(
                    content_type=self.__class__.__name__,
                    object_id=self.pk,
                    version=self.version
                ).exists()

            # Créer une nouvelle entrée de `VersionHistory`
            VersionHistory.objects.create(
                content_type=self.__class__.__name__,
                object_id=self.pk,
                version=self.version,
                data=self.to_dict()
            )
        super().save(*args, **kwargs)

    def to_dict(self):
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, datetime):
                data[field.name] = value.isoformat()  # Convertir en ISO 8601 pour les objets datetime
            elif isinstance(value, models.FileField) or isinstance(value, models.ImageField):
                # Assurez-vous que le champ a un fichier avant d'accéder à l'URL
                if value and hasattr(value, 'url'):
                    data[field.name] = value.url
                else:
                    data[field.name] = None  # Si aucun fichier n'est associé, enregistrez None
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

    def __str__(self):
        return f"{self.user.username}'s profile"