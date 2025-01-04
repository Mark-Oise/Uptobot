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
    
    context = {
        'monitor': monitor,  # Add the monitor object to the context
        'uptime': monitor.get_uptime_percentage(),
        'avg_response_time': monitor.get_average_response_time(),
        'last_checked': monitor.last_checked,
        'ssl_status': monitor.get_ssl_certificate_info(),
    }
    
    return render(request, 'dashboard/monitor/partials/monitor_metrics.html', context)
    


@login_required
def uptime_metric(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    uptime = monitor.get_uptime_percentage()
    
    response = render(request, 'dashboard/monitor/partials/uptime_metric.html', {
        'monitor': monitor,
        'uptime': uptime,
    })
    
    if uptime is None:
        # Add proper retry headers
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3'  # Limit number of retries
        response['HX-Retry-After'] = '500'  # Wait 500ms between retries
    
    return response
    return response


@login_required
def response_time_metric(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    avg_time = monitor.get_average_response_time()

    response = render(request, 'dashboard/monitor/partials/response_time_metric.html', {
        'monitor': monitor,
        'avg_time': avg_time,
    })

    if avg_time is None:
        # If response time isn't ready, tell HTMX to retry in 5 seconds
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3'  # Limit number of retries
        response['HX-Retry-After'] = '500'  # Wait 500ms between retries
      
    
    return response 


@login_required
def last_checked_metric(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    last_checked = monitor.last_checked

    response = render(request, 'dashboard/monitor/partials/last_checked_metric.html', {
        'monitor': monitor,
        'last_checked': last_checked,
    })

    if last_checked is None:
        # If last checked isn't ready, tell HTMX to retry in 5 seconds
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3'  # Limit number of retries
        response['HX-Retry-After'] = '500'  # Wait 500ms between retries
    
    
    return response 


def ssl_status_metric(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    ssl_status = monitor.get_ssl_certificate_info()
    
    response = render(request, 'dashboard/monitor/partials/ssl_status_metric.html', {
        'monitor': monitor,
        'ssl_status': ssl_status,
    })

    if ssl_status is None:
        # If ssl status isn't ready, tell HTMX to retry in 5 seconds
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3'  # Limit number of retries
        response['HX-Retry-After'] = '500'  # Wait 500ms between retries
      
    
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


def uptime_history(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)  # Add user check
    uptime_history = monitor.get_daily_uptime_history()
    
    response = render(request, 'dashboard/monitor/partials/uptime_history.html', {
        'monitor': monitor,
        'uptime_history': uptime_history,
        
    })
    
    if not uptime_history:
        # If no history data, tell HTMX to retry
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3'
       
    
    return response


def recent_incidents(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    incidents = monitor.logs.exclude(status='success').order_by('-checked_at')[:5]

    response = render(request, 'dashboard/monitor/partials/recent_incidents.html', {
        'monitor': monitor,
        'recent_incidents': incidents, 
    })
    if not incidents:
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3'  # Optional: limit number of retries
      
    
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


@login_required
def availability_indicator(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    response = render(request, 'dashboard/monitor/partials/availability_indicator.html', {
        'monitor': monitor,
    })

    if monitor.availability == 'unknown':
        response['HX-Trigger'] = 'retry-soon'
        response['HX-Retries'] = '3' 
        
    
    return response
