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
        # Use requests.Session() for connection pooling
        with requests.Session() as session:
            # More complete browser-like headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            # Try GET request first as it's more reliable
            start_time = timezone.now()
            response = session.get(
                monitor.url,
                timeout=10,
                verify=True,
                allow_redirects=True,
                headers=headers,
                stream=True
            )
            end_time = timezone.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            status = 'success' if 200 <= response.status_code < 400 else 'failure'  # Accept 3xx as success

            # Update SSL info if it's an HTTPS URL and hasn't been checked in the last 24 hours
            if (monitor.url.startswith('https') and 
                (not monitor.last_ssl_check or 
                 timezone.now() - monitor.last_ssl_check > timezone.timedelta(hours=24))):
                ssl_info = monitor.get_ssl_certificate_info()
                if ssl_info['valid']:
                    monitor.ssl_expiry_date = ssl_info['expiry_date']
                    monitor.ssl_issuer = ssl_info['issuer'] 
                    monitor.last_ssl_check = timezone.now()
                    monitor.save(update_fields=['ssl_expiry_date', 'ssl_issuer', 'last_ssl_check'])
        
            
            
            # Create log entry
            return MonitorLog.objects.create(
                monitor=monitor,
                status=status,
                response_time=response_time,
                status_code=response.status_code
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