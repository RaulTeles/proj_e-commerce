from django.urls import path
from . import views

app_name ='pedido'

urlpatterns = [
    path('', views.Pagar.as_view(), name='pagar'),
    path('fecharpedido/', views.Fecharpedido.as_view(), name='fechar'),
    path('detalhe/', views.Detalhe.as_view(), name='detalhe')
]