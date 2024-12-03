# Generated by Django 5.1.2 on 2024-11-18 19:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitor", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="monitor",
            name="custom_interval",
        ),
        migrations.AddField(
            model_name="monitor",
            name="description",
            field=models.TextField(
                blank=True, help_text="Description of the monitor.", null=True
            ),
        ),
        migrations.AddField(
            model_name="monitor",
            name="host",
            field=models.CharField(
                blank=True, help_text="Host address.", max_length=255, null=True
            ),
        ),
        migrations.AddField(
            model_name="monitor",
            name="method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("GET", "GET"),
                    ("POST", "POST"),
                    ("PUT", "PUT"),
                    ("DELETE", "DELETE"),
                    ("PATCH", "PATCH"),
                ],
                help_text="HTTP method.",
                max_length=6,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="monitor",
            name="name",
            field=models.CharField(
                default=django.utils.timezone.now,
                help_text="Monitor name",
                max_length=255,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="monitor",
            name="port",
            field=models.PositiveIntegerField(
                blank=True, help_text="Port number.", null=True
            ),
        ),
        migrations.AlterField(
            model_name="monitor",
            name="interval",
            field=models.IntegerField(
                choices=[
                    (5, "5 minutes"),
                    (10, "10 minutes"),
                    (15, "15 minutes"),
                    (30, "30 minutes"),
                    (60, "60 minutes"),
                ],
                default=5,
                help_text="Monitoring interval in minutes.",
            ),
        ),
        migrations.AlterField(
            model_name="monitor",
            name="url",
            field=models.CharField(
                blank=True, help_text="URL to monitor.", max_length=255, null=True
            ),
        ),
    ]