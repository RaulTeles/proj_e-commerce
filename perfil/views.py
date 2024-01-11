from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponse
from . import models
from . import forms
from django.contrib.auth.models import User
import copy

#criando uma classe para fazer com que as classes Criar e Update herde dela
class BasePerfil(View):
    template_name = 'perfil/create.html'
    #Criando um método setup para configurar o que será utilizado na classe
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        #criando uma variavel carrinho para qua quando o usuario trocar de senha, nao perder os dados do carrinho
        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))
        self.perfil = None

        #criando uma logica para ficiar se o usuário está logado
        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(usuario=self.request.user)
            self.contexto = {
                'userForm' : forms.UserForms(data=self.request.POST or None, usuario=self.request.user, instance=self.request.user),
                'perfilForm' :forms.PerfilForm(data=self.request.POST or None),
            }
        else:
            self.contexto = {
                'userForm' : forms.UserForms(data=self.request.POST or None),
                'perfilForm' :forms.PerfilForm(data=self.request.POST or None),
            }  

        self.userform = self.contexto['userForm']
        self.perfilform = self.contexto['perfilForm']

        self.renderizar = render(self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar

#Herdando da classe BasePerfil
class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        # if not self.userform.is_valid() or not self.perfilform.is_valid():
        if not self.userform.is_valid():
            return self.renderizar
        
        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')
    
        
        #usuário logado
        if self.request.user.is_authenticated:
            usuario = get_object_or_404(User, username=self.request.user.username)
            usuario.username = username
            
            if password:
                usuario.set_password(password)
            
            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

        #usuario não logado (novo)
        else:
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        #continuação da logica da sessão do carrinho para quando alterar a senha nao perder os itens do carrinho
        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()
        return self.renderizar

class Update(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Update')
class Login(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Login')
class Logout(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Logout')