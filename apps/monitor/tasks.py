import socket
import requests
from celery import shared_task
from datetime import datetime
from django.utils import timezone
from .models import Monitor, MonitorLog


@shared_task
def check_monitor(monitor_id):
    """
    Task to check a single monitor's status
    """
    try:
        monitor = Monitor.objects.get(id=monitor_id)
        
        if not monitor.is_active:
            return "Monitor is disabled"

        if monitor.protocol == 'HTTP':
            result = check_http(monitor)
        elif monitor.protocol == 'TCP':
            result = check_tcp(monitor)
        elif monitor.protocol == 'UDP':
            result = check_udp(monitor)
        
        # Update availability based on result
        if result.status == 'success':
            monitor.availability = 'online'
            monitor.consecutive_failures = 0
        else:
            monitor.consecutive_failures += 1
            if monitor.consecutive_failures >= monitor.alert_threshold:
                monitor.availability = 'offline'
        
        monitor.last_checked = timezone.now()
        monitor.save()
        
        return f"Check completed for {monitor.name}: {result.status}"
         
    except Monitor.DoesNotExist:
        return f"Monitor {monitor_id} not found"
    except Exception as e:
        return f"Error checking monitor {monitor_id}: {str(e)}"


def check_http(monitor):
    """Helper function to check HTTP endpoints"""
    start_time = timezone.now()
    try:
        method = getattr(requests, monitor.method.lower())
        response = method(monitor.url, timeout=10)
        response_time = (timezone.now() - start_time).total_seconds() * 1000
        
        return MonitorLog.objects.create(
            monitor=monitor,
            status='success',
            response_time=response_time,
            status_code=response.status_code
        )
    except requests.RequestException as e:
        return MonitorLog.objects.create(
            monitor=monitor,
            status='failure',
            error_message=str(e)
        )


def check_tcp(monitor):
    """Helper function to check TCP endpoints"""
    start_time = timezone.now()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((monitor.host, monitor.port))
        response_time = (timezone.now() - start_time).total_seconds() * 1000
        sock.close()
        
        return MonitorLog.objects.create(
            monitor=monitor,
            status='success',
            response_time=response_time
        )
    except socket.error as e:
        return MonitorLog.objects.create(
            monitor=monitor,
            status='failure',
            error_message=str(e)
        )
    finally:
        sock.close()


def check_udp(monitor):
    """Helper function to check UDP endpoints"""
    start_time = timezone.now()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10)
    
    try:
        # Send a dummy packet
        sock.sendto(b"ping", (monitor.host, monitor.port))
        response_time = (timezone.now() - start_time).total_seconds() * 1000
        
        return MonitorLog.objects.create(
            monitor=monitor,
            status='success',
            response_time=response_time
        )
    except socket.error as e:
        return MonitorLog.objects.create(
            monitor=monitor,
            status='failure',
            error_message=str(e)
        )
    finally:
        sock.close()


@shared_task
def schedule_monitor_checks():
    """
    Periodic task to schedule checks for all active monitors
    """
    current_time = timezone.now()
    monitors = Monitor.objects.filter(is_active=True)
    
    for monitor in monitors:
        # Check if it's time to run this monitor based on its interval
        if (not monitor.last_checked or 
            (current_time - monitor.last_checked).total_seconds() >= monitor.interval * 60):
            check_monitor.delay(monitor.id)
    
    return f"Scheduled checks for {monitors.count()} monitors"