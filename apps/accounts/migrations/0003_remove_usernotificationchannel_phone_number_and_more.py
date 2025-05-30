# Generated by Django 5.1.2 on 2025-05-16 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_remove_useralertsettings_email_alerts_enabled_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="usernotificationchannel",
            name="phone_number",
        ),
        migrations.RemoveField(
            model_name="usernotificationchannel",
            name="webhook_url",
        ),
        migrations.AddField(
            model_name="usernotificationchannel",
            name="channel_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="usernotificationchannel",
            name="oauth_token",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name="UserAlertSettings",
        ),
    ]
