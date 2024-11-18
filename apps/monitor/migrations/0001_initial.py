# Generated by Django 5.1.2 on 2024-11-18 07:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Monitor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.CharField(max_length=255)),
                (
                    "protocol",
                    models.CharField(
                        choices=[("HTTP", "HTTP"), ("TCP", "TCP"), ("UDP", "UDP")],
                        default="HTTP",
                        help_text="Protocol to monitor.",
                        max_length=4,
                    ),
                ),
                (
                    "interval",
                    models.CharField(
                        choices=[
                            (5, "5 minutes"),
                            (15, "15 minutes"),
                            (30, "30 minutes"),
                            ("custom", "Custom"),
                        ],
                        default=5,
                        help_text="Monitoring interval.",
                        max_length=10,
                    ),
                ),
                (
                    "custom_interval",
                    models.PositiveIntegerField(
                        blank=True, help_text="Custom interval in minutes.", null=True
                    ),
                ),
                (
                    "alert_threshold",
                    models.PositiveIntegerField(
                        default=3, help_text="Failures before alert is triggered."
                    ),
                ),
                (
                    "last_checked",
                    models.DateTimeField(
                        blank=True, help_text="Last check timestamp.", null=True
                    ),
                ),
                (
                    "is_online",
                    models.BooleanField(
                        default=True, help_text="Monitor active status."
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="Timestamp of creation."
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="Timestamp of last update."
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="monitors",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Monitor",
                "verbose_name_plural": "Monitors",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="MonitorLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("success", "Success"),
                            ("failure", "Failure"),
                            ("error", "Error"),
                        ],
                        help_text="Result status of the check",
                        max_length=10,
                    ),
                ),
                (
                    "response_time",
                    models.FloatField(
                        blank=True, help_text="Response time in milliseconds", null=True
                    ),
                ),
                (
                    "status_code",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        help_text="HTTP status code (for HTTP monitors)",
                        null=True,
                    ),
                ),
                (
                    "error_message",
                    models.TextField(
                        blank=True, help_text="Error details if check failed", null=True
                    ),
                ),
                (
                    "checked_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When the check was performed"
                    ),
                ),
                (
                    "monitor",
                    models.ForeignKey(
                        help_text="Associated monitor",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="logs",
                        to="monitor.monitor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Monitor Log",
                "verbose_name_plural": "Monitor Logs",
                "ordering": ["-checked_at"],
                "indexes": [
                    models.Index(
                        fields=["monitor", "checked_at"],
                        name="monitor_mon_monitor_69162d_idx",
                    ),
                    models.Index(
                        fields=["status"], name="monitor_mon_status_e82ca0_idx"
                    ),
                ],
            },
        ),
    ]
