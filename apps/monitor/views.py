from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Monitor
from .forms import AddMonitorForm, UpdateMonitorForm
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
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
    paginator = Paginator(monitors_list, 6)  # Show 6 monitors per page
    page = request.GET.get('page', 1)
    try:
        monitors = paginator.page(page)
    except:
        monitors = paginator.page(1)
    
    context = {
        'monitors': monitors,
        'form': form
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


















