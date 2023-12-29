from django.shortcuts import render
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponse

# Create your views here.
class ListaProduto(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Listar Produto')
class DetalheProduto(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detalhe Produto')
class AddToCard(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Adicionar no carrinho')
class RemoveFromCart(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Remover do carrinho')
class Cart(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Carrinho')
class Finalizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Finalizar')