from django.contrib import admin
from . import models

#Criando a classe 'inline' para mostrar toda a lista em linha
class VariacaoInline(admin.TabularInline):
    model = models.Variacao
    extra = 1

class ProdutoAdmin(admin.ModelAdmin):
    inlines = [
        VariacaoInline
    ]

# Register your models here.
admin.site.register(models.Produto, ProdutoAdmin)
admin.site.register(models.Variacao)