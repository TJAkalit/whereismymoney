from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.
@login_required(login_url="/auth/")
def index(request):
    
    return render(request, 'wim/index.html')

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
class PayView(ListView):
    
    template_name = 'wim/pay.html'
    model = Pay
    paginate_by = 10
    
    def get_context_data(self, *args, **kwargs):
        kwargs['form'] = PayForm()
        return super().get_context_data(*args, **kwargs)
    
    def post(self, request):
        
        form = PayForm(request.POST)
        if form.is_valid():
            Pay(**form.cleaned_data).save()
        
        return HttpResponseRedirect(reverse("pay"))
    