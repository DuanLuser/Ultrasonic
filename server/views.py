import json
import logging
from logzero import setup_logger, LogFormatter

from django.shortcuts import redirect, render
from django.http import HttpResponse,JsonResponse,Http404
from django.shortcuts import get_list_or_404
from django.utils import timezone
from .models import Device, Log
from .forms import DeviceForm
from rest_framework import viewsets,permissions
from dwebsocket.decorators import accept_websocket,require_websocket
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User

formatter = LogFormatter(datefmt=logging.Formatter.default_time_format)
logger = setup_logger(name=__name__, level=logging.INFO, formatter=formatter)

# raspberrypi address
# HOST = ''
# POST = [21566, 21567]

ONLINE_DEVICES=dict()

@login_required(login_url='login')
def index(request):
    device_list = Device.objects.all()
    LOGS = Log.objects.order_by('-time')
    #logs_10 = LOGS[:10]
    return render(request,'index.html',locals())

@login_required(login_url='login')
def device_list(request):
    device_list = Device.objects.all()
    LOGS = Log.objects.order_by('-time')
    #logs_10 = LOGS[:10]
    return render(request,'device_list.html',locals())

@login_required(login_url='login')
def logs(request):
    #Log.objects.all().delete()
    LOGS = Log.objects.order_by('-time')
    #logs_10 = LOGS[:10]
    return render(request,'logs.html',locals())

@login_required(login_url='login')
def logs_detail(request, device_id):
    try:
        device = Device.objects.get(pk=device_id)
        #logs_10 = Log.objects.order_by('-time')[:10]
        device_logs = Log.objects.filter(device_id = device_id).order_by('-time')
        form = DeviceForm(instance=device)
        return render(request,'logs_detail.html', locals())
    except: 
        raise Http404("设备不存在！")

@login_required(login_url='login')
def device_detail(request, device_id):
    try:
        device = Device.objects.get(pk=device_id)
        #logs_10 = Log.objects.order_by('-time')[:10]
        #device_logs = Log.objects.filter(device_id = device_id).order_by('-time')
        form = DeviceForm(instance=device)
        return render(request,'device_detail.html', locals())
    except: 
        raise Http404("设备不存在！")

@login_required(login_url='login')
def device_action(request, device_id, action):
    return HttpResponse(f'{device_id},{action}')

@login_required(login_url='login')
def reset(request, device_id):
    device = Device.objects.get(pk=device_id)
    device.order_todo = 'reset'
    device.save()

    form = DeviceForm(instance=device)
    return render(request,'device_detail.html', locals())


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # 跳转到成功页面
            return redirect(index)
        else:
            # 返回一个非法登录的错误页面
            return render(request, 'login.html', {'message': '用户名或密码不正确！'})
    else:
        return render(request, 'login.html')

# 登出
def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return redirect(login_view)

'''
#@require_websocket
def wsapi(request, device_id):

    try:
        # 设备连接处理
        logger.info(f"设备 id={device_id} 通过WebSocket连接")
        # 查询对应id的设备
        devices = Device.objects.filter(device_id = device_id)

        # 错误id处理
        if len(devices) != 1:
            resp = {'type':'error','message':'Wrong device id'}
            request.websocket.send(json.dumps(resp))
            logger.warning(f"没有id={device_id}的设备！")
            request.websocket.close()
            logger.info(f"设备 id={device_id} 已断开")

        device = devices[0]
        resp = {'type':'success','message':'Welcome, ' + device.device_name }
        request.websocket.send(json.dumps(resp))
        logger.info(f"设备信息：id={device_id} name={device.device_name} lastonline={device.last_online_time}")

        # 修改最新上线时间
        device.last_online_time = timezone.now()
        device.device_status = 'online'
        device.save()

        # 记录日志
        log = Log(device_id=device, level='info', message='设备上线')
        log.save()

        ONLINE_DEVICES[device_id] = request.websocket

        while True:
            message = request.websocket.wait()  # 接受前端发送来的数据
            if message:
                # 消息处理
                message = bytes.decode(message)
                logger.info(message)
                Log(device_id=device, level='info', message=message).save() # 记录日志
            else:
                # 断开连接处理
                Log(device_id=device, level='info', message='设备离线').save() # 记录日志
                device.device_status = 'offline' # 修改设备状态
                device.save() # 持久化
                break
    finally:
        request.websocket.close()
        ONLINE_DEVICES.pop(device_id, None)
        logger.info(f"设备 id={device_id} WebSocket连接断开")
'''





















