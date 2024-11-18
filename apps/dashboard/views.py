from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def dashboard_home(request):
    return render(request, 'dashboard/dashboard_home.html')

# @login_required
# def profile_edit(request):
#     return render(request, 'dashboard/profile_edit.html')