from django.urls import path
from . import views

# URL config
urlpatterns = [
    path('', views.browseComputerLists),
    path('windows/<str:host>/', views.windowsHostPage),
    path('windows/<str:host>/logout', views.windowsLogout),
    path('windows/<str:host>/eventlog', views.windowsViewEventLog),
    path('windows/<str:host>/services', views.windowsGetServices),
    path('windows/<str:host>/services/<str:service>', views.windowsSetServiceStartup),
    path('windows/<str:host>/services/<str:service>/start', views.windowsStartService),
    path('windows/<str:host>/services/<str:service>/restart', views.windowsRestartService),
    path('windows/<str:host>/services/<str:service>/stop', views.windowsStopService),
    path('windows/<str:host>/services/<str:service>/pause', views.windowsPauseService),
    path('windows/<str:host>/tools', views.windowsHostTools),
    path('windows/<str:host>/network', views.windowsHostTools),
    path('windows/<str:host>/accounts', views.windowsHostTools),
    path('windows/<str:host>/drives', views.windowsHostTools),
]
