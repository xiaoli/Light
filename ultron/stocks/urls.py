from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('api/v1/get_history_by_stock/', views.get_history_by_stock, name='get_history_by_stock'),
    path('api/v1/get_history_by_date/', views.get_history_by_date, name='get_history_by_date'),
    path('', views.index, name='index')
]