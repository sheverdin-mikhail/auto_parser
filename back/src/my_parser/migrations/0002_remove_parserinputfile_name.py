# Generated by Django 4.1 on 2022-08-14 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_parser', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parserinputfile',
            name='name',
        ),
    ]