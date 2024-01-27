from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from .models import Pedido, ItemPedido

from produto.models import Variacao
from utils import utils

#Criando uma classe para verificar se o usuário está criado para acessar uma outra classe
class DispatchRequiredLoginMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return super().dispatch(request, *args, **kwargs)
    #Criando um método para fazer com que só apareça os pedidos do usuário que realizou eles

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(usuario=self.request.user)
        return qs
class Pagar(DispatchRequiredLoginMixin, DetailView):
        template_name = 'pedido/pagar.html'
        model = Pedido
        pk_url_kwarg = 'pk'
        context_object_name = 'pedido'


        

class SalvarPedido(View):
    template_name = 'pedido/pagar.html'

    def get(self, *args, **kwargs):
        #checagem se o usuário não está logado
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer o Login.'
            )
            return redirect ('perfil:criar')

        #Checando se o carrinho possui algum produtod
        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'O carrinho está vazio!'
            )
            return redirect ('produto:lista')
        #checando se a quantidade de variacoes do produto do carrinho ainda tem em estoque
        carrinho = self.request.session.get('carrinho')
        carrinho_variacao_ids = [v for v in carrinho]

        #Selecionando os produtos do carrinho para poder manipular
        #passando o .selecte_related('Produto') para diminuir a requisição no SQL
        bd_variacoes = list (Variacao.objects.select_related('Produto').filter(id__in=carrinho_variacao_ids))
        

        for variacao in bd_variacoes:
            vid = str(variacao.id)
            estoque = variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unit = carrinho[vid]['preco_unitario']
            preco_unit_promocional = carrinho[vid]['preco_unitario_promocional']

            error_msg_estoque = ''

            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unit
                carrinho[vid]['preco_quantitativo_promocional'] = estoque * preco_unit_promocional

                error_msg_estoque ='Estoque insuficiente para alguns produtos do seu carrinho. Reduzimos a quantidade desses produtos. Por favor, verifique novamente o seu carrinho antes de confirmar a compra.'

            if error_msg_estoque:
                messages.error(
                    self.request,
                    error_msg_estoque
                )
                self.request.session.save()
                return redirect('produto:carrinho')
        qtd_total_carrinho = utils.cart_total_qtd(carrinho)    
        valor_total_carrinho = utils.cart_totals(carrinho)  
        #Registrando o pedido
        pedido = Pedido(
            usuario=self.request.user,
            total = valor_total_carrinho,
            qtd_total = qtd_total_carrinho,
            status='C',
        ) 

        pedido.save()

        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],
                ) for v in carrinho.values()
            ]
        )
        contexto = {

        }
        
        del self.request.session['carrinho']
        return redirect(
            reverse(
                'pedido:pagar',
                kwargs = {
                    'pk': pedido.pk
                }
            )
        )
        # return render(self.request, self.template_name, contexto)
class Detalhe(DispatchRequiredLoginMixin, DetailView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/detalhe.html'
    pk_url_kwarg = 'pk'
    
class Lista(DispatchRequiredLoginMixin, ListView):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedido/lista.html'
    paginate_by = 5
    ordering = ['-id']