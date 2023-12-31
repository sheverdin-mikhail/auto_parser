# Generated by Django 4.1 on 2022-10-10 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_parser', '0012_remove_parsertask_output_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='parseroutputtask',
            name='holding_balance',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Остаток Холдинга (свободный)'),
        ),
        migrations.AddField(
            model_name='parseroutputtask',
            name='holding_expense',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Расход Холдинга'),
        ),
        migrations.AddField(
            model_name='parseroutputtask',
            name='implemented',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Можно реализовать в ИМ'),
        ),
    ]