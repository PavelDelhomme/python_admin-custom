# Generated by Django 5.1.2 on 2024-11-04 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_core', '0002_customchart'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255, unique=True)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
    ]
