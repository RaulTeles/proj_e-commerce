from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
import re
from utils.validacpf import valida_cpf

# Create your models here.
class Perfil(models.Model):
    usuario = models.OneToOneField(User,on_delete=models.CASCADE, verbose_name = 'Usuário')
    idade = models.PositiveIntegerField()
    data_nascimento = models.DateField(auto_now=False, auto_now_add=False)
    cpf = models.CharField(max_length=11, verbose_name = 'CPF')
    endereco = models.CharField(max_length=50, verbose_name = 'Endereço')
    numero = models.CharField(max_length=6, verbose_name = 'Número')
    complemento = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=8, verbose_name = 'CEP')
    cidade = models.CharField(max_length=30)
    estados = models.CharField(
        default = 'AC',
        max_length=2,
        choices=(
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),
        )
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.usuario.first_name} {self.usuario.last_name}'

    #validando alguns campos do model com o método clean
    def clean(self):
        error_messages={

        }

        if not valida_cpf(self.cpf):
            error_messages['cpf'] = 'Digite um CPF válido'
        if re.search(r'[^0-9]', self.cep) or len(self.cep) < 8:
            error_messages['cep'] = 'CEP Inválido, digite apenas números'
        if error_messages:
            raise ValidationError(error_messages)
