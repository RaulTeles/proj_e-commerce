from django.contrib import admin
from . import models

#criando a classe 'inline' para mostrar toda a lista em linha
class ItemPedidoInline(admin.TabularInline):
    model = models.ItemPedido
    extra = 1

class PedidoAdmin(admin.ModelAdmin):
    inlines = [
        ItemPedidoInline
    ]

# Register your models here.
admin.site.register(models.Pedido, PedidoAdmin)
admin.site.register(models.ItemPedido)