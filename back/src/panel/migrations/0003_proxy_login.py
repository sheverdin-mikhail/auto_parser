# Generated by Django 4.1 on 2022-11-23 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0002_alter_proxy_options_alter_siteuser_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='proxy',
            name='login',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Логин'),
        ),
    ]
