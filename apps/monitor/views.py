from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Monitor
from .forms import AddMonitorForm, UpdateMonitorForm
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
            return redirect('monitor:monitor_list')
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
    return render(request, 'dashboard/monitor/monitor_list.html', context)


@login_required
def monitor_detail(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    
    # Get initial chart data (7 days by default)
    response_time_data = monitor.get_response_time_data(period='7d')
    chart_data = {
        'dates': [entry['date'].strftime('%d %b') if hasattr(entry['date'], 'strftime') 
                 else entry['date'] for entry in response_time_data],
        'data': [round(entry['avg_response_time'], 2) for entry in response_time_data]
    }
    
    context = {
        'monitor': monitor,
        'form': UpdateMonitorForm(instance=monitor),
        'recent_incidents': monitor.logs.exclude(status='success').order_by('-checked_at')[:5],
        'health_score': monitor.get_health_score(),
        'health_status': monitor.get_health_status(),
        'chart_data': chart_data,
    }
    
    return render(request, 'dashboard/monitor/monitor_detail.html', context)


@login_required
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
    return render(request, 'dashboard/monitor/monitor_list_items.html', context)


def delete_monitor(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    monitor.delete()
    messages.success(request, 'Monitor deleted successfully')
    return redirect('monitor:monitor_list')


@login_required
def settings(request):
    return render(request, 'dashboard/monitor/settings.html')


@login_required
def response_time_chart(request, slug):
    monitor = get_object_or_404(Monitor, slug=slug, user=request.user)
    period = request.GET.get('period', '7d')
    
    try:
        data = monitor.get_response_time_data(period)
        
        # Format data for ApexCharts
        categories = [entry['date'].strftime('%d %b') for entry in data]
        series = [round(entry['avg_response_time'], 2) for entry in data]
        
        context = {
            'categories': categories,
            'series': series,
            'period': period
        }
        
        return render(request, 'dashboard/monitor/charts.html', context)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)






