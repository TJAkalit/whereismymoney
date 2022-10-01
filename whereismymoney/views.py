from datetime import date, datetime, timedelta
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
    data['month_begin'] = datetime(today.year, today.month, 1, 0, 0, 0, 0)
    for i in range(1, 32):
        if (data['month_begin'] + timedelta(days=i)).month!=data['month_begin'].month:
            data['month_end'] = data['month_begin'] + timedelta(days=i) - timedelta(microseconds=1)
            break
    
    data['month_begin_fmt'] = data['month_begin'].strftime("%d.%m.%Y")
    data['month_end_fmt'] = data['month_end'].strftime("%d.%m.%Y")
    data['percent'] = data['today'].day / data['month_end'].day * 100
    
    for i, t in (('income', 0, ), ('outcome', 1)):
        data[i] = Pay.objects.filter(
            type__type=t, 
            date__gt=data['month_begin'], 
            date__lt=data['month_end'],
        ).aggregate(Sum('cost'))["cost__sum"]
        if not data[i]:
            data[i] = 0
    
    data['pays_summ_by_category'] = Pay.objects.filter(type__type=1)\
        .values('type__name').annotate(total=Sum('cost'))

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
from django.views.generic.dates import DayArchiveView
@method_decorator(login_required, name='dispatch')
class PayView(DayArchiveView):
    
    queryset = Pay.objects.all()
    date_field = "date"
    allow_future = True
    allow_empty = True
    template_name = 'wim/pay.html'
    
    def get_context_data(self, **kwargs):
        
        kwargs['form'] = PayForm()
        kwargs = super().get_context_data(**kwargs)
        kwargs['daily_income'] = 0
        kwargs['daily_outcome'] = 0
        for item in kwargs['object_list']:
            if item.type.type == 0:
                kwargs['daily_income'] += item.cost
            if item.type.type == 1:
                kwargs['daily_outcome'] += item.cost
        kwargs['daily_result'] = kwargs['daily_income'] - kwargs['daily_outcome']
        for i in ('previous_day', 'next_day'):
            kwargs[i +'_link'] = reverse(
                'pay',
                kwargs={
                    "year": kwargs[i].year,
                    "month": kwargs[i].strftime("%b"),
                    "day": kwargs[i].day,
                },
            )
        return kwargs
    
    def get(self, request, *args, **kwargs):
        
        for i in ('year', 'month', 'day',):
            if i not in kwargs:
                
                return HttpResponseRedirect(
                    reverse(
                        'pay',
                        kwargs={
                            "year": date.today().year,
                            "month": date.today().strftime("%b"),
                            "day": date.today().day,
                        },
                    )
                )    
        return super().get(request, *args, **kwargs)
    
    def post(self, request):
        
        form = PayForm(request.POST)
        if form.is_valid():
            Pay(user = request.user, **form.cleaned_data).save()
        
        return HttpResponseRedirect(
            reverse(
                'pay',
                kwargs={
                    "year": date.today().year,
                    "month": date.today().strftime("%b"),
                    "day": date.today().day,
                },
            )
        )    
    
    