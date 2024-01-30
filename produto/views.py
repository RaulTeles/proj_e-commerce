from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from . import models
from perfil.models import Perfil
from django.db.models import Q



# Create your views here.
class ListaProduto(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 6
    ordering = ['-id']

class Busca(ListaProduto):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo') or self.request.sessio['termo']
        qs = super().get_queryset(*args, **kwargs)

        if not termo:
            return qs
        
        self.request.sessio['termo'] = termo


        qs = qs.filter(
            Q(nome__contains=termo)|
            Q(descricao_curta=termo)|
            Q(descricao_longa=termo)
        )
        self.request.session.save()
        return qs

class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'

class AddToCard(View):
    def get(self, *args, **kwargs):
        # if self.request.session.get('carrinho'):
        #     del self.request.session['carrinho']
        #     self.request.session.save()
            
        # o selfe...META['HTTP_REFERER'] serve para redirecioanar o usuário para a página anterior
        http_referer = self.request.META.get('HTTP_REFERER',reverse('produto:lista'))
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            messages.error(
                self.request,
                'O Produto não existe!'
            )
            return redirect (http_referer)
            
        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        variacao_estoque = variacao.estoque
        produto = variacao.Produto
        
        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        if imagem:
            imagem = imagem.name
        else:
            imagem = ''

        if variacao_estoque < 1:
            messages.error(
                self.request,
                'Estoque Insuficiente'
            )
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']

        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1

            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque insuficiente para {quantidade_carrinho}x no produto "{produto_nome}". Adicionamos {variacao_estoque}x no seu carrinho.'
                )
                quantidade_carrinho = variacao_estoque
            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * quantidade_carrinho
        else:
            carrinho[variacao_id] = {
                'produto_id' : produto_id,
                'produto_nome' : produto_nome,
                'variacao_nome' : variacao_nome,
                'variacao_id' : variacao_id,
                'preco_unitario' : preco_unitario,
                'preco_unitario_promocional' : preco_unitario_promocional,
                'preco_quantitativo' : preco_unitario,
                'preco_quantitativo_promocional' : preco_unitario_promocional,
                'quantidade' : 1,
                'slug' : slug,
                'imagem' : imagem,
            }
        self.request.session.save()
        messages.success(
            self.request,
            f'O produto {produto_nome} {variacao_nome}, foi adicionado com sucesso ao seu carrinho {carrinho[variacao_id]["quantidade"]}x.'
            
        )
        return redirect(http_referer)
    
    
class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get('HTTP_REFERER',reverse('produto:lista'))
        variacao_id = self.request.GET.get('vid')
        
        if not variacao_id:
            return redirect (http_referer)
        
        #Checando se o carrinho existe

        if not self.request.session.get('carrinho'):
            return redirect (http_referer)
        
        #checando se o id que a pessoa está tentando remover do carrinho, está realmente no carrinho.
        if variacao_id not in self.request.session['carrinho']:
            return redirect (http_referer)
        
        carrinho = self.request.session['carrinho'][variacao_id]
        messages.success(
            self.request,
            f'O produto {carrinho["produto_nome"]} "{carrinho["variacao_nome"]}", foi removido do seu carrinho.'
        )

        #removendo do carrinho pela variação do ID
        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()

        return redirect(http_referer)

class Carrinho(View):
    def get(self, *args, **kwargs):
        contexto = {'carrinho':self.request.session.get('carrinho', {})
        }
        return render(
            self.request,
            'produto/carrinho.html', contexto
            )
        
class ResumoDaCompra(View):
    def get(self, *args, **kwargs):
        #criando um decarator, para que essa view só seja acessada para usuários logados
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        
        #checando se o cliente possui o perfil completo cadastrado antes de efetuar a compra
        perfil = Perfil.objects.filter(usuario=self.request.user).exists()

        if not perfil:
            messages.error(
                self.request,
                'Usuário sem Perfil.'
            )
            return redirect('perfil:criar')
        
        #criando uma logica para não permitir o usuario chear no resumo da compra sem item no carrinho

        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Seu carrinho está vazio!'
            )
            return redirect('produto:lista')
        

        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
        }

        return render (self.request, 'produto/resumo.html', contexto)