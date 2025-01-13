from django.shortcuts import render

# Create your views here.
def subscription(request):
    return render(request, 'dashboard/subscription.html')