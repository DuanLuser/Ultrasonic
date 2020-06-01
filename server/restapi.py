from .models import Device, Log
from .serializers import LogSerializer,DeviceSerializer
from rest_framework import permissions
from rest_framework import serializers,viewsets,filters,routers


class DeviceViewSet(viewsets.ModelViewSet):
    
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    def get_queryset(self):
        queryset = self.queryset
        machineid = self.request.query_params.get('deviceid')
        if machineid != None:
            queryset = queryset.filter(device_id__exact = int(machineid))
        return queryset


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer

    def get_queryset(self):
        queryset = self.queryset
        machineid = self.request.query_params.get('deviceid')
        if machineid != None and machineid != 'all':
            queryset = queryset.filter(device_id__exact = int(machineid))
        if machineid == 'all':
            queryset = Log.objects.all()
        
        return queryset


router = routers.DefaultRouter()
router.register('device', DeviceViewSet)
router.register('log', LogViewSet)


