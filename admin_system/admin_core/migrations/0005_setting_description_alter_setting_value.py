# Generated by Django 5.1.2 on 2024-11-04 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_core', '0004_customchart_last_modified_customchart_version_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='setting',
            name='value',
            field=models.TextField(),
        ),
    ]
