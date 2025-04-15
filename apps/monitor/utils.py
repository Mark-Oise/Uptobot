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

    uptime = monitor.get_uptime_percentage()
    avg_response_time = monitor.get_average_response_time()
    last_checked = monitor.last_checked
    ssl_status = monitor.get_ssl_certificate_info()
    
    response = render(request, 'dashboard/monitor/partials/monitor_metrics.html', {
        'monitor': monitor,
        'uptime': uptime,
        'avg_response_time': avg_response_time,
        'last_checked': last_checked,
        'ssl_status': ssl_status,
    })
    
    # Only trigger reload if there's no data AND no failed checks
    if (uptime is None or avg_response_time is None):
        response['HX-Trigger'] = 'metrics-loading'
    
    return response
    



@login_required
def monitor_health_score(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)

    health_score = monitor.get_health_score()
    health_status = monitor.get_health_status()
        
    response = render(request, 'dashboard/monitor/partials/monitor_health_score.html', {
        'monitor': monitor,
        'health_score': health_score,
        'health_status': health_status,
    })

    # Only trigger reload if no data AND no failed checks
    if (monitor.get_uptime_percentage() is None or 
        monitor.get_average_response_time() is None):
        response['HX-Trigger'] = 'health-score-loading'
    
    return response


def monitor_tab_content(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)

    uptime_history = monitor.get_daily_uptime_history()
    recent_incidents = monitor.logs.exclude(status='success').order_by('-checked_at')[:5]
    
    response = render(request, 'dashboard/monitor/partials/tab_content.html', {
        'monitor': monitor,
        'uptime_history': uptime_history,
        'recent_incidents': recent_incidents,
    })
    
    # Only trigger reload if no data AND no failed checks
    if uptime_history is None:
        response['HX-Trigger'] = 'tab-content-loading'
    
    return response



@login_required
def response_time_chart(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    response_time_data = monitor.get_response_time_data(period='7d')
    
    context = {
        'monitor': monitor,
        'chart_data': {
            'dates': [entry['date'].strftime('%d %b') if hasattr(entry['date'], 'strftime') 
                     else entry['date'] for entry in response_time_data],
            'data': [round(entry['avg_response_time'], 2) for entry in response_time_data]
        }
    }
    
    response = render(request, 'dashboard/monitor/partials/charts.html', context)
    
    # Only trigger reload if no data AND no failed checks
    if not response_time_data and not monitor.has_failed_checks:
        response['HX-Trigger'] = 'chart-loading'
    
    return response



