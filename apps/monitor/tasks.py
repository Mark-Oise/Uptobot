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
    try:
        # Only check SSL info once per day
        should_check_ssl = False
        if monitor.url.startswith('https'):
            last_ssl_check = getattr(monitor, 'last_ssl_check', None)
            if not last_ssl_check or (timezone.now() - last_ssl_check).days >= 1:
                should_check_ssl = True
        
        # Use requests.Session() for connection pooling
        with requests.Session() as session:
            # Measure only the actual request time
            start_time = timezone.now()
            response = session.request(
                monitor.method,
                monitor.url, 
                timeout=10,
                verify=True,  # Re-enable SSL verification
                allow_redirects=True
            )
            end_time = timezone.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            status = 'success' if 200 <= response.status_code < 300 else 'failure'
            
            # Check SSL only if needed
            ssl_info = None
            if should_check_ssl:
                ssl_info = monitor.get_ssl_info()
                monitor.last_ssl_check = timezone.now()
                monitor.save(update_fields=['last_ssl_check'])
            
            # Create log entry
            log = MonitorLog.objects.create(
                monitor=monitor,
                status=status,
                response_time=response_time,
                status_code=response.status_code
            )
            
            # Add SSL warning if there are issues
            if ssl_info and not ssl_info['valid']:
                log.error_message = f"Warning: {ssl_info['error']} (Site still accessible)"
                log.status = 'warning'
                log.save()
                
            return log
            
    except requests.exceptions.SSLError as e:
        # More detailed SSL error handling
        error_msg = str(e)
        if "certificate verify failed" in error_msg:
            error_msg = "SSL certificate validation failed. Certificate may be self-signed or missing intermediate certificates."
        elif "certificate has expired" in error_msg:
            error_msg = "SSL certificate has expired."
        
        return MonitorLog.objects.create(
            monitor=monitor,
            status='warning',  # Changed from 'error' to 'warning'
            error_message=f"SSL Warning: {error_msg}"
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