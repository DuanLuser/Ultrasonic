from django.db import models
import django.utils.timezone as timezone

# Create your models here.


class Device(models.Model):
    device_id = models.CharField(verbose_name='设备ID', max_length=50, primary_key=True)
    device_name = models.CharField(verbose_name='监管区域', max_length=100, default='测试区域')
    description = models.TextField(verbose_name='描述', blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_online_time = models.DateTimeField(verbose_name='上一次上线时间',auto_now_add=True)#default = None)

    DEVICE_STATUS = (('offline','离线'),('online','在线'),('malfunction','故障'))
    device_status = models.CharField(verbose_name='设备状态', choices=DEVICE_STATUS, max_length=50, default='offline', editable=False)
    
    #information of detecting
    OUTCOME = (('default',''),('nonempty','非空'),('empty','空'))    
    outcome = models.CharField(verbose_name='结果', choices=OUTCOME, max_length=50, default='default', editable=False)
    angle = models.CharField(verbose_name='角度', max_length=20, default='', editable=False)
    distance = models.CharField(verbose_name='距离', max_length=20, default='', editable=False)

    RESET_STATUS = (('no', '未重置'),('yes','已重置'))
    reset_status = models.CharField(verbose_name='重置状态', choices=RESET_STATUS, max_length=50, default='no', editable=False)
    order_todo = models.CharField(verbose_name='命令', max_length=50, default='', editable=False)
    order_outcome = models.CharField(verbose_name='命令结果', max_length=50, default='', editable=False)


    def __str__(self):
        return self.device_name


class Log(models.Model):
    LOG_CHOICES = (('info', '信息'), ('purpose', '提示'), ('warning', '警告'), ('error', '错误'))
    device_id = models.ForeignKey('Device', on_delete=models.CASCADE) #device
    level = models.CharField(verbose_name='类型', choices=LOG_CHOICES, max_length=50, default='info')
    message = models.CharField(verbose_name='内容', max_length=50)
    time = models.DateTimeField(verbose_name='时间', auto_now_add=True)
    area = models.CharField(verbose_name='监管区域', max_length=50, default='')

    def __str__(self):
        return f'{self.time}|{self.level}|{self.message}'



