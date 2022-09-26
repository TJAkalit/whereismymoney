from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    class Meta:
        ordering = ('id',)
    
    types = ('Доход', 'Расход',)
    
    id = models.IntegerField(
        primary_key=True,
    )
    name = models.CharField(
        verbose_name='Категория затрат',
        max_length=512,
    )
    type = models.IntegerField(
        verbose_name='Тип денежного движения',
        choices=enumerate(types),
        null=False,
        blank=False,
    )
    
    def get_type(self):
        for i, name in enumerate(self.types):
            if i == self.type: return name
        return 'Неизвестно'
    
    def __str__(self):
        return self.name
    
    def get_color(self):
        if self.type == 0: return '--bs-green'
        elif self.type == 1: return '--bs-red'
        else: return '--bs-blue'
    
class Pay(models.Model):
    class Meta:
        ordering = ('id',)
        
    id = models.IntegerField(primary_key=True)
    type = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        verbose_name='Категория',
    )
    cost = models.FloatField(
        verbose_name='Сумма',
        null=False,
        blank=False,
    )
    name = models.CharField(
        'Пояснение', blank=False, null=False,
        max_length=128,
    )
    date = models.DateTimeField(
        verbose_name='Дата',
        auto_now_add=True,
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    
    def get_type(self):
        return self.type.get_type()