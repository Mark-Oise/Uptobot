from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Monitor
from .forms import AddMonitorForm
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.



def monitor_list(request):
    monitors = Monitor.objects.filter(user=request.user)
    
    context = {
        'monitors': monitors,
        'form': AddMonitorForm()
    }
    return render(request, 'dashboard/monitor/monitor_list.html', context)



def monitor_detail(request, pk):
    monitor = get_object_or_404(Monitor, pk=pk, user=request.user)
    
    # Get recent incidents (non-successful logs)
    recent_incidents = monitor.logs.exclude(status='success').order_by('-checked_at')[:5]
    
    context = {
        'monitor': monitor,
        'uptime_percentage': monitor.get_uptime_percentage(),
        'avg_response_time': monitor.get_average_response_time(),
        'ssl_info': monitor.get_ssl_info(),
        'recent_incidents': recent_incidents,
    }
    
    return render(request, 'dashboard/monitor/monitor_detail.html', context)



def add_monitor(request):
    if request.method == 'POST':
        form = AddMonitorForm(request.POST)
        if form.is_valid():
            monitor = form.save(commit=False)
            monitor.user = request.user
            monitor.save()
            messages.success(request, 'Monitor added successfully')
            return redirect('monitor:monitor_list')
    else:
        form = AddMonitorForm()
    
    return render(request, 'dashboard/monitor/add_monitor.html', {'form': form})



def search_monitors(request):
    search_query = request.GET.get('search', '').strip()
    monitors = Monitor.objects.filter(user=request.user)
    
    if search_query:
        monitors = monitors.filter(
            Q(name__icontains=search_query) |
            Q(url__icontains=search_query)
        )
    
    context = {
        'monitors': monitors,
        'search_query': search_query,
    }
    return render(request, 'dashboard/monitor/monitor_list_items.html', context)



def settings(request):
    return render(request, 'dashboard/monitor/settings.html')




