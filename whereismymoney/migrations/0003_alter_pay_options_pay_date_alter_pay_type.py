# Generated by Django 4.1.1 on 2022-09-25 21:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('whereismymoney', '0002_alter_category_options_alter_category_type_pay'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pay',
            options={'ordering': ('id',)},
        ),
        migrations.AddField(
            model_name='pay',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pay',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='whereismymoney.category', verbose_name='Категория'),
        ),
    ]
