from .models import Log,Device
from rest_framework import serializers

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = "__all__"
        #fields = ('device_id', 'level', 'time', 'message')
        #owner = serializers.ReadOnlyField(source='owner.username')

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
        #fields = ('device_id', 'device_name','status', 'description', 'create_time', 'last_online_time','device_outcome')
        #owner = serializers.ReadOnlyField(source='owner.username')
