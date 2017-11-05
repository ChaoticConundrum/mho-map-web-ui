from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^version/$', views.psb_version),
    url(r'^data_range/(?P<start>[0-9]+)/(?P<end>[0-9]+)/$', views.data_range),
    url(r'^current_data/(?P<device_id>[0-9]+)/', views.current_data),
    url(r'^topology/', views.topology),
    url(r'^devices/', views.devices),
    url(r'^drivers/', views.drivers),
    url(r'^device/', views.device),
]
