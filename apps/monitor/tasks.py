import requests
from celery import shared_task
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

        result = check_http(monitor)
        
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
        response = method(
            monitor.url, 
            timeout=10,
            verify=True,  # Always verify SSL certificates
            allow_redirects=True  # Follow redirects
        )
        response_time = (timezone.now() - start_time).total_seconds() * 1000
        
        # Get SSL info if HTTPS
        ssl_info = monitor.get_ssl_info() if monitor.url.startswith('https') else None
        
        # Check if status code is successful (2xx)
        if 200 <= response.status_code < 300:
            status = 'success'
        else:
            status = 'failure'
        
        log = MonitorLog.objects.create(
            monitor=monitor,
            status=status,
            response_time=response_time,
            status_code=response.status_code
        )
        
        # Store SSL info in error_message if there are issues
        if ssl_info and not ssl_info['valid']:
            log.error_message = f"SSL Certificate Issue: {ssl_info['error']}"
            log.save()
            
        return log
        
    except requests.exceptions.SSLError as e:
        return MonitorLog.objects.create(
            monitor=monitor,
            status='error',
            error_message=f"SSL Certificate Error: {str(e)}"
        )
    except requests.exceptions.Timeout:
        return MonitorLog.objects.create(
            monitor=monitor,
            status='failure',
            error_message="Request timed out"
        )
    except requests.exceptions.ConnectionError:
        return MonitorLog.objects.create(
            monitor=monitor,
            status='failure',
            error_message="Failed to establish connection"
        )
    except requests.RequestException as e:
        return MonitorLog.objects.create(
            monitor=monitor,
            status='failure',
            error_message=str(e)
        )


@shared_task
def schedule_monitor_checks():
    """
    Periodic task to schedule checks for all active monitors
    """
    current_time = timezone.now()
    monitors = Monitor.objects.filter(is_active=True)
    
    for monitor in monitors:
        if (not monitor.last_checked or 
            (current_time - monitor.last_checked).total_seconds() >= monitor.interval * 60):
            check_monitor.delay(monitor.id)
    
    return f"Scheduled checks for {monitors.count()} monitors"