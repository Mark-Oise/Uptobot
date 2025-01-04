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
    
    response = render(request, 'dashboard/monitor/partials/monitor_metrics.html', {
        'monitor': monitor,
        'uptime': monitor.get_uptime_percentage(),
        'avg_response_time': monitor.get_average_response_time(),
        'last_checked': monitor.last_checked,
        'ssl_status': monitor.get_ssl_certificate_info(),
        
       
    })
    
    if monitor.get_uptime_percentage() is None or monitor.get_average_response_time() is None:
        response['HX-Trigger'] = 'metrics-loading'
    
    return response
    



@login_required
def monitor_health_score(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
        
    response = render(request, 'dashboard/monitor/partials/monitor_health_score.html', {
        'monitor': monitor,
        'health_score': monitor.get_health_score(),
        'health_status': monitor.get_health_status(),
    })

    # Check if underlying metrics that determine health score are ready
    # trigger a reload of the health score section via HTMX Triggers. This ensures the UI
    # updates once the underlying metrics are ready to calculate an accurate 
    # health score.
    if monitor.get_uptime_percentage() is None or monitor.get_average_response_time() is None:
        response['HX-Trigger'] = 'health-score-loading'
    
    return response


def monitor_tab_content(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    response = render(request, 'dashboard/monitor/partials/tab_content.html', {
        'monitor': monitor,
        'uptime_history': monitor.get_daily_uptime_history(),
        'recent_incidents': monitor.logs.exclude(status='success').order_by('-checked_at')[:5],
    })
    
    
    if monitor.get_uptime_percentage() is None:
        response['HX-Trigger'] = 'tab-content-loading'
    
    return response









@login_required
def response_time_chart(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    # Get initial chart data (7 days by default)
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
    
    # Check if we have any data points
    if not response_time_data:
        response['HX-Trigger'] = 'chart-loading'
    
    return response



