# Generated by Django 2.1 on 2020-04-21 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0011_log_area'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='area',
        ),
    ]
