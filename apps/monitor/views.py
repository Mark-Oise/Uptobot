from django.shortcuts import render
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
    }
    return render(request, 'dashboard/monitor/monitor_list.html', context)



def monitor_detail(request, pk):
    monitor = get_object_or_404(Monitor, pk=pk, user=request.user)
    return render(request, 'dashboard/monitor/monitor_detail.html', {'monitor': monitor})



def create_monitor(request):
    if request.method == 'POST':
        form = MonitorForm(request.POST)
        if form.is_valid():
            monitor = form.save(commit=False)
            monitor.user = request.user
            monitor.save()
            return redirect('monitor_list')
    else:
        form = MonitorForm()
    
    return render(request, 'monitor/create_monitor.html', {'form': form})
