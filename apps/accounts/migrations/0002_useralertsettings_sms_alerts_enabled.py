# Generated by Django 5.1.2 on 2024-12-22 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="useralertsettings",
            name="sms_alerts_enabled",
            field=models.BooleanField(default=False),
        ),
    ]