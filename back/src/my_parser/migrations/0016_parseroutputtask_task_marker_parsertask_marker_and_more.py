# Generated by Django 4.1 on 2022-12-09 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_parser', '0015_parseroutputtask_task_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='parseroutputtask',
            name='task_marker',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Поле для выборки'),
        ),
        migrations.AddField(
            model_name='parsertask',
            name='marker',
            field=models.CharField(choices=[('1', 'Аналитика'), ('2', 'Наличие')], default='1', max_length=2, verbose_name='Маркер'),
        ),
        migrations.AlterField(
            model_name='parseroutputtask',
            name='stock',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Склад'),
        ),
    ]