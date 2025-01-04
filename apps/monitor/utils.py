from .models import Monitor
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required



def search_monitors(request):
    search_query = request.GET.get('search', '').strip()
    monitors_list = Monitor.objects.filter(user=request.user)
    
    if search_query:
        monitors_list = monitors_list.filter(
            Q(name__icontains=search_query) |
            Q(url__icontains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(monitors_list, 6)  # Show 6 monitors per page
    page = request.GET.get('page', 1)
    try:
        monitors = paginator.page(page)
    except:
        monitors = paginator.page(1)
    
    context = {
        'monitors': monitors,
        'search_query': search_query,
    }
    return render(request, 'dashboard/monitor_list_items.html', context)


def delete_monitor(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    monitor.delete()
    messages.success(request, 'Monitor deleted successfully')
    return redirect('monitor:monitor_list')


@login_required
def monitor_metrics(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    # Get all metrics
    uptime = monitor.get_uptime_percentage()
    avg_response_time = monitor.get_average_response_time()
    last_checked = monitor.last_checked
    ssl_status = monitor.get_ssl_certificate_info()
    availability = monitor.availability 
    
    # Check if all data is ready
    all_ready = all([uptime is not None, 
                    avg_response_time is not None,
                    last_checked is not None,
                    ssl_status is not None,
                    availability != 'unknown']) 
    
    response = render(request, 'dashboard/monitor/partials/monitor_metrics.html', {
        'monitor': monitor,
        'uptime': uptime,
        'avg_response_time': avg_response_time,
        'last_checked': last_checked,
        'ssl_status': ssl_status,
    })
    
    if not all_ready:
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '10'  # Allow more retries since we're checking all metrics
        response['HX-Retry-After'] = '500'  # Wait 2 seconds between retries
    
    return response
    



def monitor_health_score(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    health_score = monitor.get_health_score()
    health_status = monitor.get_health_status() if health_score is not None else None
    
    context = {
        'monitor': monitor,
        'health_score': health_score,
        'health_status': health_status,
        'has_data': health_score is not None
    }
    
    response = render(request, 'dashboard/monitor/partials/monitor_health_score.html', context)
    
    if health_score is None:
        # If health score isn't ready, tell HTMX to retry in 5 seconds
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3'  # Limit number of retries
        response['HX-Retry-After'] = '500'  # Wait 500ms between retries
    
    
    return response


def monitor_tab_content(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    # Get both uptime history and recent incidents
    uptime_history = monitor.get_daily_uptime_history()
    incidents = monitor.logs.exclude(status='success').order_by('-checked_at')[:5]
    
    response = render(request, 'dashboard/monitor/partials/tab_content.html', {
        'monitor': monitor,
        'uptime_history': uptime_history,
        'recent_incidents': incidents,
    })
    
    # If either data set is missing, trigger a retry
    if not uptime_history and not incidents:
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3'
        response['HX-Retry-After'] = '2000'  # Wait 2 seconds between retries
    
    return response









@login_required
def response_time_chart(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    # Get initial chart data (7 days by default)
    response_time_data = monitor.get_response_time_data(period='7d')
    chart_data = {
        'dates': [entry['date'].strftime('%d %b') if hasattr(entry['date'], 'strftime') 
                 else entry['date'] for entry in response_time_data],
        'data': [round(entry['avg_response_time'], 2) for entry in response_time_data]
    }
    
    response = render (request, 'dashboard/monitor/partials/charts.html', {
        'monitor': monitor,
        'chart_data': chart_data,
    })

    response['HX-Trigger'] = 'retry-soon'
    response['HX-Retries'] = '3'

    return response



