from django.urls import path
from . import views

#quando for chamar alguma url no template deve-se utilizar: produto:lista ou outro que seja
app_name = 'produto'

urlpatterns = [
    path('', views.ListaProduto.as_view(), name='lista'),
    path('<slug>', views.DetalheProduto.as_view(), name='detalhe'),
    path('addtocard/', views.AddToCard.as_view(), name='add'),
    path('removefromcard/',views.RemoverDoCarrinho.as_view(), name='remove'),
    path('carrinho/', views.Carrinho.as_view(), name='carrinho'),
    path('resumo/', views.ResumoDaCompra.as_view(), name='resumo'),
    path('busca/', views.Busca.as_view(), name='busca'),

]
