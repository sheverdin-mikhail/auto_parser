# Generated by Django 4.1 on 2022-11-23 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_parser', '0014_parsersite_alter_parseroutputtask_finds_list_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parseroutputtask',
            name='task_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID исходной задачи'),
        ),
    ]
