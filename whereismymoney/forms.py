from django import forms

class AuthForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    login = forms.CharField(
        label='Логин', 
        max_length=32,
        
    )
    password = forms.CharField(label='Пароль', max_length=128)

from .models import Category    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('type', 'name',)
    
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
from .models import Pay
class PayForm(forms.ModelForm):
    class Meta:
        model = Pay
        fields = ('type', 'name', 'cost')
            
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'