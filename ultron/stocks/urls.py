from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('api/v1/get_history_by_stock/', views.get_history_by_stock, name='get_history_by_stock'),
    path('api/v1/get_history_by_date/', views.get_history_by_date, name='get_history_by_date'),
    path('list_strategy', views.list_strategy, name='list_strategy'),
    path('calculate', views.calculate, name='calculate'),
    path('list_khistory', views.list_khistory, name='list_khistory'),
    path('', views.index, name='index')
]