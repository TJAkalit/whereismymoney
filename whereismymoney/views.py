from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.views.generic.dates import DayMixin
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.db.models import Sum

# Create your views here.
@login_required(login_url="/auth/")
def index(request):
    
    template_name = 'wim/index.html'
    data = dict()
    today = datetime.now()
    data['today'] = today
    data['month_begin'] = datetime(today.year, today.month, 1, 0, 0, 0, 0, today.tzinfo)
    for i in range(1, 32):
        if (data['month_begin'] + timedelta(days=i)).month!=data['month_begin'].month:
            
            data['month_end'] = data['month_begin'] + timedelta(days=i) - timedelta(microseconds=1)
            break
    
    data['month_begin_fmt'] = data['month_begin'].strftime("%d.%m.%Y")
    data['month_end_fmt'] = data['month_end'].strftime("%d.%m.%Y")
    data['percent'] = data['today'].day / data['month_end'].day * 100
    data['income'] = Pay.objects.filter(
        type__type=0, 
        date__gt=data['month_begin'], 
        date__lt=data['month_end'],
    ).aggregate(Sum('cost'))["cost__sum"]
    data['outcome'] = Pay.objects.filter(
        type__type=1, 
        date__gt=data['month_begin'], 
        date__lt=data['month_end'],
    ).aggregate(Sum('cost'))["cost__sum"]
    
    
    return render(request, template_name, data)

@login_required(login_url="/auth/")
def exit(request):
    
    if request.user:
        logout(request)
        
    return HttpResponseRedirect(reverse('auth'))

from .forms import AuthForm
class LoginView(TemplateView):
    
    template_name = 'wim/auth.html'

    def get(self, request):
        
        form = AuthForm()
        
        return render(request, self.template_name, {"form": form})
    
    def post(self, request):
        
        form = AuthForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        
        user = authenticate(
            username=form.cleaned_data['login'], 
            password=form.cleaned_data['password'],
        )
        
        if not user:
            return render(request, self.template_name, {"form": form})
        
        login(request, user)
        
        return HttpResponseRedirect(request.GET.get("next", "/"))

from .models import Category
from .forms import CategoryForm
@method_decorator(login_required, name='dispatch')
class CategoryView(ListView):
    
    template_name = 'wim/category.html'
    model = Category
    paginate_by = 10
    
    def get_context_data(self, *args, **kwargs):
        kwargs['form'] = CategoryForm()
        return super().get_context_data(*args, **kwargs)
    
    def post(self, request):
        
        form = CategoryForm(request.POST)
        if form.is_valid():
            Category(**form.cleaned_data).save()
        
        return HttpResponseRedirect(reverse("category"))

from .models import Pay
from .forms import PayForm
@method_decorator(login_required, name='dispatch')
class PayView(ListView):
    
    template_name = 'wim/pay.html'
    model = Pay
    paginate_by = 10
    
    def get_context_data(self, *args, **kwargs):
        kwargs['form'] = PayForm()
        income = Pay.objects.filter(type__type=0).aggregate(Sum('cost'))
        outcome = Pay.objects.filter(type__type=1).aggregate(Sum('cost'))
        kwargs['summ'] = income['cost__sum'] - outcome['cost__sum']
        
        return super().get_context_data(*args, **kwargs)
    
    def paginate_queryset(self, queryset, page_size):
        qs = super().paginate_queryset(queryset, page_size)
        income = 0
        outcome = 0
        for item in qs[2]:
            if item.type.type==0:
                income+=item.cost
            if item.type.type==1:
                outcome+=item.cost
        qs[1].page_summ = income - outcome
        qs[1].page_income = income
        qs[1].page_outcome = outcome
        return qs
    
    def post(self, request):
        
        form = PayForm(request.POST)
        if form.is_valid():
            Pay(user=request.user, **form.cleaned_data).save()
        
        return HttpResponseRedirect(reverse("pay"))
    