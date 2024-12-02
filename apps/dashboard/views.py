from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.monitor.forms import AddMonitorForm
from apps.monitor.models import Monitor


@login_required
def dashboard_home(request):
    monitors = Monitor.objects.filter(user=request.user)
    
    context = {
        'form': AddMonitorForm(),
        'monitors': monitors,
        'total_monitors': monitors.count(),
        'active_monitors': monitors.filter(is_active=True).count(),
    }
    return render(request, 'dashboard/dashboard_home.html', context)

# @login_required
# def profile_edit(request):
#     return render(request, 'dashboard/profile_edit.html')