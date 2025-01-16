from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'landing/index.html')


def privacy_policy(request):
    return render(request, 'landing/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'landing/terms_of_service.html')


def refund_policy(request):
    return render(request, 'landing/refund_policy.html')