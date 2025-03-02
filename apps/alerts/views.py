from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

def email_incident(request):
    return render(request, 'alerts/batched_alerts.html')