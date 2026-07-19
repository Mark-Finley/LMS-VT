from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from patients.models import Patient
from test_catalogue.models import Test
from requests.models import TestRequest
from billing.models import Invoice
from samples.models import Sample
from results.models import Result
import json
import datetime
from django.utils import timezone
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from billing.models import Payment
from requests.models import RequestedTest

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'dashboard/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    # Fetch data for dashboard UI panels
    patients = Patient.objects.all().order_by('-created_at')[:10]
    tests = Test.objects.filter(status='active')
    requests = TestRequest.objects.all().order_by('-request_date')[:15]
    invoices = Invoice.objects.all().order_by('-created_at')[:15]
    samples = Sample.objects.all().order_by('-created_at')[:15]
    
    # Context data for page rendering
    context = {
        'user': request.user,
        'patients': patients,
        'tests': tests,
        'requests': requests,
        'invoices': invoices,
        'samples': samples,
    }
    return render(request, 'dashboard/index.html', context)

class DashboardMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.localdate()
        start_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
        
        # Today's Patients (registered today)
        today_patients_count = Patient.objects.filter(created_at__gte=start_of_day).count()
        
        # Today's Revenue (payments today)
        revenue_sum = Payment.objects.filter(payment_date__gte=start_of_day).aggregate(Sum('amount_paid'))['amount_paid__sum']
        today_revenue = float(revenue_sum) if revenue_sum is not None else 0.0
        
        # Pending Results (results that are in draft or reviewed)
        pending_results_count = Result.objects.filter(status__in=[Result.STATUS_DRAFT, Result.STATUS_REVIEWED]).count()
        
        # Completed Tests (tests with status completed, verified, released)
        completed_tests_count = RequestedTest.objects.filter(
            status__in=[
                RequestedTest.STATUS_COMPLETED,
                RequestedTest.STATUS_VERIFIED,
                RequestedTest.STATUS_RELEASED
            ]
        ).count()
        
        # Critical Results
        critical_results_count = Result.objects.filter(is_critical=True).count()
        
        # Build metrics response
        metrics = {
            'today_patients': today_patients_count,
            'today_revenue': today_revenue,
            'pending_results': pending_results_count,
            'completed_tests': completed_tests_count,
            'critical_results': critical_results_count,
            'low_stock_alerts': 0,      # Phase 2 inventory
            'equipment_offline': 0      # Phase 2 equipment
        }
        
        return Response(metrics)

