# Generated by Django 2.1 on 2020-04-21 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0008_auto_20200421_1128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='time_limit',
        ),
        migrations.RemoveField(
            model_name='log',
            name='type_limit',
        ),
        migrations.AddField(
            model_name='device',
            name='time_limit',
            field=models.CharField(default='', max_length=50, verbose_name='时间限制'),
        ),
        migrations.AddField(
            model_name='device',
            name='type_limit',
            field=models.CharField(default='', max_length=50, verbose_name='类型限制'),
        ),
    ]
