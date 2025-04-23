from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Monitor
from .forms import AddMonitorForm, UpdateMonitorForm
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.notifications.models import Notification

# Create your views here.


@login_required
def monitor_list(request):
    if request.method == 'POST':
        form = AddMonitorForm(request.POST)
        if form.is_valid():
            monitor = form.save(commit=False)
            monitor.user = request.user
            monitor.save()
            messages.success(request, 'Monitor added successfully')
            return redirect(reverse('monitor:monitor_detail', kwargs={'slug': monitor.slug}))
        else:
            messages.error(request, 'Please correct the errors below.')
            # Print form errors to console for debugging
            print(form.errors)
    else:
        form = AddMonitorForm()
    
    # Add pagination
    monitors_list = Monitor.objects.filter(user=request.user)
    total_monitors = monitors_list.count()
    paginator = Paginator(monitors_list, 6)  # Show 6 monitors per page
    page = request.GET.get('page', 1)
    try:
        monitors = paginator.page(page)
    except:
        monitors = paginator.page(1)

    # Get current month stats
    active_monitors = monitors_list.filter(is_active=True)
    total_uptime = 0
    total_response_time = 0
    active_count = active_monitors.count()

    for monitor in active_monitors:
        uptime = monitor.get_uptime_percentage(days=30)
        if uptime is not None:
            total_uptime += uptime

        response_time = monitor.get_average_response_time(days=30)
        if response_time is not None:
            total_response_time += response_time

    current_uptime = round(total_uptime / active_count, 2) if active_count > 0 else 0
    current_response_time = round(total_response_time / active_count, 2) if active_count > 0 else 0

    # Get last month stats
    last_month = timezone.now() - timedelta(days=30)
    last_month_monitors = monitors_list.filter(created_at__lte=last_month)
    last_month_count = last_month_monitors.count()
    
    # Calculate last month's uptime and response time
    last_month_active = last_month_monitors.filter(is_active=True)
    last_month_active_count = last_month_active.count()
    last_month_uptime = 0
    last_month_response_time = 0

    for monitor in last_month_active:
        uptime = monitor.get_uptime_percentage(days=30)
        if uptime is not None:
            last_month_uptime += uptime

        response_time = monitor.get_average_response_time(days=30)
        if response_time is not None:
            last_month_response_time += response_time

    last_month_avg_uptime = round(last_month_uptime / last_month_active_count, 2) if last_month_active_count > 0 else 0
    last_month_avg_response_time = round(last_month_response_time / last_month_active_count, 2) if last_month_active_count > 0 else 0

    # Calculate percentage changes
    monitor_growth = round(((total_monitors - last_month_count) / last_month_count * 100) if last_month_count > 0 else 100, 1)
    uptime_growth = round(((current_uptime - last_month_avg_uptime) / last_month_avg_uptime * 100) if last_month_avg_uptime > 0 else 100, 1)
    response_time_growth = round(((current_response_time - last_month_avg_response_time) / last_month_avg_response_time * 100) if last_month_avg_response_time > 0 else 100, 1)
    
    context = {
        'monitors': monitors,
        'form': form,
        'total_monitors': total_monitors,
        'avg_uptime': current_uptime,
        'avg_response_time': current_response_time,
        'monitor_growth': monitor_growth,
        'uptime_growth': uptime_growth,
        'response_time_growth': response_time_growth
    }
    return render(request, 'dashboard/monitor_list.html', context)


@login_required
def monitor_detail(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = UpdateMonitorForm(request.POST, instance=monitor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Monitor updated successfully')
            return redirect(reverse('monitor:monitor_detail', kwargs={'slug': monitor.slug}))
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UpdateMonitorForm(instance=monitor)
    
    # Get initial chart data (7 days by default)
    response_time_data = monitor.get_response_time_data(period='7d')
    chart_data = {
        'dates': [entry['date'].strftime('%d %b') if hasattr(entry['date'], 'strftime') 
                 else entry['date'] for entry in response_time_data],
        'data': [round(entry['avg_response_time'], 2) for entry in response_time_data]
    }
    
    context = {
        'monitor': monitor,
        'form': form,
        'recent_incidents': monitor.logs.exclude(status='success').order_by('-checked_at')[:5],
        'health_score': monitor.get_health_score(),
        'health_status': monitor.get_health_status(),
        'chart_data': chart_data,
    }
    
    return render(request, 'dashboard/monitor_detail.html', context)


















