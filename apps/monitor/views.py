from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Monitor
from .forms import AddMonitorForm
# Create your views here.



def monitor_list(request):
    monitors = Monitor.objects.filter(user=request.user)
    paginator = Paginator(monitors, 10)  # Show 10 monitors per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_monitors': monitors.count(),
        'active_monitors': monitors.filter(is_online=True).count(),
        'form': AddMonitorForm(),
    }
    return render(request, 'dashboard/monitor/monitor_list.html', context)



def monitor_detail(request, pk):
    monitor = get_object_or_404(Monitor, pk=pk, user=request.user)
    return render(request, 'dashboard/monitor/monitor_detail.html', {'monitor': monitor})



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


def protocol_fields(request):
    protocol = request.GET.get('protocol', 'HTTP')
    context = {
        'protocol': protocol,
        'method_choices': Monitor.METHOD_CHOICES if protocol == 'HTTP' else None,
    }
    return render(request, 'dashboard/monitor/protocol_fields.html', context)
