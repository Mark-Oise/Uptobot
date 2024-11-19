from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.monitor.forms import AddMonitorForm

@login_required
def dashboard_home(request):
    context = {
        'form': AddMonitorForm(),
    }
    return render(request, 'dashboard/dashboard_home.html', context)

# @login_required
# def profile_edit(request):
#     return render(request, 'dashboard/profile_edit.html')