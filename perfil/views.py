from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponse
from . import models
from . import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
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
            self.perfil = models.Perfil.objects.filter(usuario=self.request.user).first()
            self.contexto = {
                'userForm' : forms.UserForms(data=self.request.POST or None, usuario=self.request.user, instance=self.request.user),

                'perfilForm' :forms.PerfilForm(data=self.request.POST or None, instance=self.perfil),
            }
        else:
            self.contexto = {
                'userForm' : forms.UserForms(data=self.request.POST or None),
                'perfilForm' :forms.PerfilForm(data=self.request.POST or None),
            }  

        self.userform = self.contexto['userForm']
        self.perfilform = self.contexto['perfilForm']

        #renderizar a pagina especifica quando o usuario já estiver logado e for atualizar o perfil
        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'

        self.renderizar = render(self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar

#Herdando da classe BasePerfil
class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
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

            if not self.perfil:
                self.perfilform.cleaned_data['usuario'] = usuario
                perfil = models.Perfil(**self.perfilform.cleaned_data)
                perfil.save()
            else:
                perfil = self.perfilform.save(commit=False)
                perfil.usuario = usuario
                perfil.save()

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

        #criando uma lógica para qua quando o usuário altere alguma informação do seu perfil, ele não perca as informações do carrinho
        if password:
            autentica = authenticate(self.request,
                                    username=usuario.username,
                                    password=password)
            
            if autentica:
                login(self.request, user=usuario)

        #Logica para que se em algum momento exclua um perfil de usuario, com ele logado, possa recriar sem erro

        #continuação da logica da sessão do carrinho para quando alterar a senha nao perder os itens do carrinho
        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()

        messages.success(
            self.request,
            'Seu Cadastro foi criado/atualizado com Sucesso!'
        )
        return redirect('perfil:criar')
        # return self.renderizar

class Update(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Update')
class Login(View):
    #criando método de post
    def post(self, *args, **kwargs):
            #checando se o username foi enviado
            username = self.request.POST.get('usuario')
            password = self.request.POST.get('senha')
            if not username or not password:
                messages.error(
                    self.request,
                    'Usuário ou senha inválidos'
                )
                return redirect('perfil:criar')
            usuario = authenticate(self.request, username=username, password=password)

            if not usuario:
                messages.error(
                self.request,
                'Usuário ou senha inválidos'
            )
                return redirect('perfil:criar')
            login(self.request, user=usuario)
            messages.success(
                self.request,
                'Login feito com sucesso!'
            )
            return redirect('produto:carrinho')
            
    
class Logout(View):
    def get(self, *args, **kwargs):
        #criando variável para não perder o carrinho quando fizer o logout
        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))
        self.perfil = None
        logout(self.request)
        self.request.session['carrinho'] = self.carrinho
        self.request.session.save()
        return redirect("produto:lista")