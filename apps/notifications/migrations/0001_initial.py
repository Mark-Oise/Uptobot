# Generated by Django 5.1.2 on 2025-01-03 15:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("monitor", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
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
                ("title", models.CharField(max_length=255)),
                ("message", models.TextField()),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("availability", "Availability"),
                            ("response_time", "Response Time"),
                            ("ssl_expiry", "SSL Expiry"),
                            ("monitor_down", "Monitor Down"),
                            ("monitor_up", "Monitor Up"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("info", "Information"),
                            ("warning", "Warning"),
                            ("critical", "Critical"),
                        ],
                        db_index=True,
                        default="info",
                        max_length=10,
                    ),
                ),
                ("is_read", models.BooleanField(db_index=True, default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("action_url", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "monitor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notifications",
                        to="monitor.monitor",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "-created_at"],
                        name="notificatio_user_id_05b4bc_idx",
                    ),
                    models.Index(
                        fields=["user", "is_read", "-created_at"],
                        name="notificatio_user_id_f2ad08_idx",
                    ),
                ],
            },
        ),
    ]
