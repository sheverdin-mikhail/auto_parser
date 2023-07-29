# Generated by Django 4.1 on 2022-08-18 13:29

from django.db import migrations, models
import src.base.services


class Migration(migrations.Migration):

    dependencies = [
        ('my_parser', '0004_alter_parserinputfile_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='parsertask',
            name='rows_count',
            field=models.IntegerField(blank=True, default=0, verbose_name='Количество заданий'),
        ),
        migrations.AlterField(
            model_name='parsertask',
            name='output_file',
            field=models.FileField(blank=True, null=True, upload_to=src.base.services.get_path_output_file, verbose_name='Выходящие данные парсера'),
        ),
        migrations.AlterField(
            model_name='parsertask',
            name='status',
            field=models.CharField(choices=[('ready', 'Готов к выполнению'), ('run', 'Выполняется'), ('done', 'Выполнен')], default='ready', max_length=255, verbose_name='Статус работы парсера'),
        ),
    ]
