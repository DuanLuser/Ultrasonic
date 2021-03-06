# Generated by Django 2.1 on 2020-05-03 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0013_log_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='angle',
            field=models.CharField(default='', editable=False, max_length=20, verbose_name='角度'),
        ),
        migrations.AddField(
            model_name='device',
            name='distance',
            field=models.CharField(default='', editable=False, max_length=20, verbose_name='距离'),
        ),
        migrations.AlterField(
            model_name='device',
            name='device_status',
            field=models.CharField(choices=[('offline', '离线'), ('online', '在线'), ('malfunction', '故障')], default='offline', editable=False, max_length=50, verbose_name='设备状态'),
        ),
        migrations.AlterField(
            model_name='device',
            name='last_online_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='上一次上线时间'),
        ),
        migrations.AlterField(
            model_name='device',
            name='order_outcome',
            field=models.CharField(default='', editable=False, max_length=50, verbose_name='命令结果'),
        ),
        migrations.AlterField(
            model_name='device',
            name='order_todo',
            field=models.CharField(default='', editable=False, max_length=50, verbose_name='命令'),
        ),
        migrations.AlterField(
            model_name='device',
            name='outcome',
            field=models.CharField(choices=[('default', ''), ('nonempty', '非空'), ('empty', '空')], default='default', editable=False, max_length=50, verbose_name='结果'),
        ),
        migrations.AlterField(
            model_name='device',
            name='reset_status',
            field=models.CharField(choices=[('no', '未重置'), ('yes', '已重置')], default='no', editable=False, max_length=50, verbose_name='重置状态'),
        ),
    ]
