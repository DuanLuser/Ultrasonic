from django.core.management.base import BaseCommand, CommandError           
from server.models import Device, Log

from socket import *
from multiprocessing import Pool
import django.utils.timezone as timezone

portlist = [21566,21567,21568,21569,21570,21571]
Info = ['设备上线', '设备离线', '设备已重置', '目标区域空旷', '有新增物体, 在', '物体被清理，目标区域空旷', '新增物体被移至']
Angle = ['左侧','前方','右侧']
online_time=timezone.now()

def addLog(msg, device, level):
    log = Log()
    log.device_id=device
    log.level=level
    log.message=msg
    log.area=device.device_name
    log.save()

def shutdown(device):
    device.device_status = 'offline'  
    device.outcome='default'
    device.distance=device.angle=''
    device.reset_status='no'


def dealwith(server_port):
    server = server_port[0]
    ID = server_port[1] - portlist[0] + 1
    online_flag = False
    try:
        server.settimeout(10)
        conn,addr = server.accept() # 等电话打进来，每个conn代表一个客户端的连接    
        print(conn)    
        print('the call has comming')  
        #devices = Device.objects.filter(device_id = ID)
        #device = devices[0]
        device = Device.objects.get(pk=ID)
        device.order_todo = 'connect'
        device.outcome = 'default'
        device.device_status = 'offline'
        device.save()    
 
        try:
            server.settimeout(10)
            print('port', ID,'order', device.order_todo)
            conn.send(device.order_todo.encode(encoding='utf-8'))       
            data_c = conn.recv(1024)
            print(data_c.decode())
            flag = 0
            if data_c.decode() == 'connectOK':
                device.device_status = 'online'
                device.save()
                online_flag = True
                online_time=timezone.now()
                addLog(Info[0], device, 'info')  #上线
                data_r = conn.recv(1024)
                print(data_r.decode())
                if data_r.decode() == 'resetOK':
                    device.reset_status='yes' 
                    addLog(Info[2], device, 'info')  #重置
                    flag = 1
            if flag == 1 :
                conn.send('detect'.encode(encoding='utf-8'))  
                data_d = conn.recv(1024)
                print(data_d.decode())
                count = 0
                log_empty = False
                log_nonempty = False
                prior_distance = -1.00 ##
                prior_angle1 = -1
                prior_angle2 = -1
                while data_d.decode() == 'detectOK':
                    data_o = conn.recv(1024)
                    print(data_o.decode())
                    if not data_o:
                        shutdown(device)
                        device.last_online_time = online_time
                        device.save()              
                        addLog(Info[1], device, 'info')  #离线 
                        break  

                    out = data_o.decode()
                    angle1 = 1  # default: 前方
                    angle2 = 1
                    distance = '0.00m'
                    nonempty_flag = False
                    if out=='empty' or out.index('nonempty')>=0 or out=='default':
                        display=out
                        if len(out)>8 and out.index('nonempty')>=0:
                            angle1=int(out[9:12])
                            angle2=int(out[13:16])
                            distance=out[17:22]
                            display='nonempty'
                            nonempty_flag = True

                        device.angle=out[9:16]
                        device.distance=distance
                        device.outcome=display
                        device.save()
                        count += 1
                        if count ==1 and out=='empty':
                            addLog(Info[3], device, 'purpose')  # 
                            prior_distance = -1.00 ##
                            prior_angle1 = -1
                            prior_angle2 = -1
                            log_empty = True
                        elif count ==1 and nonempty_flag == True:
                            info = Info[4]+"角度为"+str(angle1)+'-'+str(angle2)+"°, 距离为"+distance
                            addLog(info, device, 'warning')  # 
                            prior_distance = float(distance[0:4]) ##
                            prior_angle1 = angle1
                            prior_angle2 = angle2
                            log_nonempty = True
                        elif count >1 and out=='empty' and log_nonempty == True:
                            addLog(Info[5], device, 'purpose')  # 
                            prior_distance = -1.00 ##
                            prior_angle1 = -1
                            prior_angle2 = -1
                            log_empty = True
                            log_nonempty = False
                        elif count >1 and nonempty_flag == True and log_empty == True:
                            info = Info[4]+"角度为"+str(angle1)+'-'+str(angle2)+"°, 距离为"+distance
                            addLog(info, device, 'warning')  # 
                            prior_distance = float(distance[0:4]) ##
                            prior_angle1 = angle1
                            prior_angle2 = angle2
                            log_nonempty = True 
                            log_empty = False 
                        elif count >1 and nonempty_flag == True and log_nonempty == True:
                            cur_distance = float(distance[0:4])
                            if abs(prior_angle1-angle1)>5 or abs(prior_angle2-angle2)>5 or abs(cur_distance-prior_distance) > 0.10:
                                info = Info[6]+"角度为"+str(angle1)+'-'+str(angle2)+"°, 距离为"+distance
                                addLog(info, device, 'warning')  # 
                                prior_distance = cur_distance
                                prior_angle1 = angle1
                                prior_angle2 = angle2
                                log_nonempty = True 
                                log_empty = False     
                             
        except:
            print('None device') 
            shutdown(device)
            if online_flag == True: 
                device.last_online_time = online_time
            device.save() 
            addLog(Info[1], device, 'info')  #离线
        dealwith(server_port)

    except:
        print('timeout',ID)
        device1 = Device.objects.get(pk=ID)
        shutdown(device1)
        if online_flag == True: 
                device1.last_online_time = online_time
        device1.save() 
        dealwith(server_port)
    

class Command(BaseCommand):
    def handle(self, *args, **options):  
        print('start')
        servers = []       
        for port in portlist:
            addr = ('', port)
            server = socket(AF_INET, SOCK_STREAM)
            server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            server.bind(addr)
            server.listen(2)
            servers.append((server,port))

        while True:
            with Pool(len(portlist)) as p:
                p.map(dealwith,servers)








