# Generated by Django 2.1 on 2020-06-06 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0015_auto_20200514_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='angle',
            field=models.CharField(default='', editable=False, max_length=35, verbose_name='角度'),
        ),
        migrations.AlterField(
            model_name='device',
            name='distance',
            field=models.CharField(default='', editable=False, max_length=35, verbose_name='距离'),
        ),
    ]
