from django.core.management.base import BaseCommand, CommandError           
from server.models import Device, Log

from socket import *
from multiprocessing import Pool
import django.utils.timezone as timezone

portlist = [21566,21567,21568,21569,21570,21571]
Info = ['设备上线', '设备离线', '设备已重置', '目标区域空旷', '新增物体', '物体均被清理', ]

online_time=timezone.now()

#abs(prior_angle1-angle1)>5 or abs(prior_angle2-angle2)>5 or abs(cur_distance-prior_distance) > 0.10:

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

def compareOut(prior_out,cur_out,site_num):
    cur_equal = [0, 0, 0, 0, 0]
    prior_equal = [0, 0, 0, 0, 0]
    for i in range(0, site_num):
        min_a=int(cur_out[i][0:3])
        max_a=int(cur_out[i][4:7])
        d=float(cur_out[i][8:12])
        for t in range(0, 5):
            if prior_out[t] != "0-0,-1" and prior_equal[t] == 0:
                pmin_a=int(prior_out[t][0:3])
                pmax_a=int(prior_out[t][4:7])
                pd=float(prior_out[t][8:12])
                if abs(pmin_a-min_a) <=3 and abs(pmax_a-max_a) <=3 and abs(pd-d)<0.10:
                   cur_equal[i]=1
                   prior_equal[t]=1
                   break
    return cur_equal, prior_equal

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
                prior_out = ["0-0,-1","0-0,-1","0-0,-1","0-0,-1","0-0,-1"] #5
                prior_num = 0

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
                    angle=""
                    distance=""
                    cur_out = ["","","","",""] # 5

                    site_num=-1
                    nonempty_flag = False
                    if out=='empty' or out.index('nonempty')>=0 or out=='default':
                        display=out
                        if len(out)>8 and out.index('nonempty')>=0:
                            site_num=int(out[len(out)-1])
                            if site_num > 5:
                                site_num = 5
                            for i in range(0,site_num):
                                cur_out[i]=out[(9+i*14):(21+i*14)]
                                angle+=cur_out[i][0:7]+","
                                distance+=cur_out[i][8:12]+","
                            display='nonempty'
                            nonempty_flag = True

                        device.angle=angle+str(site_num)
                        device.distance=distance
                        device.outcome=display
                        device.save()
                        count += 1
                        if count ==1 and out=='empty':
                            addLog(Info[3], device, 'purpose')  # 
                            prior_out = ["0-0,-1","0-0,-1","0-0,-1","0-0,-1","0-0,-1"] #5
                            prior_num = 0
                            log_empty = True
                        elif count ==1 and nonempty_flag == True:
                            info = "有"+str(site_num)+"个"+Info[4]
                            addLog(info, device, 'warning')  # 
                            prior_out = ["0-0,-1","0-0,-1","0-0,-1","0-0,-1","0-0,-1"] #5
                            for i in range(0,site_num):
                                prior_out[i]=cur_out[i]
                            prior_num = site_num
                            log_nonempty = True
                        elif count >1 and out=='empty' and log_nonempty == True:
                            addLog(Info[5]+"，"+Info[3], device, 'purpose')  # 
                            prior_out = ["0-0,-1","0-0,-1","0-0,-1","0-0,-1","0-0,-1"] #5
                            prior_num = 0
                            log_empty = True
                            log_nonempty = False
                        elif count >1 and nonempty_flag == True and log_empty == True:
                            info = info = "有"+str(site_num)+"个"+Info[4]
                            addLog(info, device, 'warning')  # 
                            prior_out = ["0-0,-1","0-0,-1","0-0,-1","0-0,-1","0-0,-1"] #5
                            for i in range(0,site_num):
                                prior_out[i]=cur_out[i]
                            prior_num = site_num
                            log_nonempty = True 
                            log_empty = False 
                        elif count >1 and nonempty_flag == True and log_nonempty == True:
                            cur_equal, prior_equal=compareOut(prior_out, cur_out, site_num)
                            new_add = 0
                            old_minus = 0
                            for i in range(0, site_num):
                                if cur_equal[i]==0:
                                    new_add+=1
                            for i in range(0, 5):
                                if prior_out[i]!="0-0,-1" and prior_equal[i]==0:
                                    old_minus+=1
                            if  new_add !=0 or old_minus !=0 :
                                info = ""
                                if new_add !=0:
                                    info += "新增"+str(new_add)+"个，"
                                if old_minus !=0:
                                    info += "移走"+str(old_minus)+"个，"
                                prior_num=prior_num+new_add-old_minus
                                info += "目前存在"+str(prior_num)+"个新增物体"
                                addLog(info, device, 'warning')  # 
                                prior_out = ["0-0,-1","0-0,-1","0-0,-1","0-0,-1","0-0,-1"] #5
                                for i in range(0,site_num):
                                    prior_out[i]=cur_out[i]
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








