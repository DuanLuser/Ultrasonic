from django.urls import path,include
from . import views
from . import restapi
from rest_framework import routers


urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('device', views.device_list, name='device_list'),
    path('device/<int:device_id>', views.device_detail, name='device_detail'),
    path('device/<int:device_id>/<str:action>', views.device_action, name='device_action'),
    path('logs', views.logs, name='logs'),
    path('logs/<int:device_id>', views.logs_detail, name='logs_detail'),

    path('device/<int:device_id>/reset/', views.reset, name='reset'),

    path('api/', include(restapi.router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    #path('wsapi/<int:device_id>', views.wsapi, name='wsapi'),

]
