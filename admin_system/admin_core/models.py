from django.db import models
from django.contrib.auth import get_user_model


class ProjectSetting(models.Model):
   key = models.CharField(max_length=255, unique=True)
   value = models.TextField()
   description = models.TextField(blank=True, null=True)


   def __str__(self):
       return f"{self.key} : {self.value}"




User = get_user_model()

class CustomChart(models.Model):
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