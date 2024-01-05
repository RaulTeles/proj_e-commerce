#arquivo omfilter criando para formatar o valor de dinheiro apresentado nos cards dos produtos.
#necessário criar o arquivo __init__ para o python entender e iniciar esse arquivo
#é necessario que esses arquivos estejam em uma pasta chamada templatestags
from django.template import Library
from utils import utils

register = Library()

@register.filter
def formata_preco(val):
    return utils.formata_preco(val)

@register.filter
def cart_total_qtd(carrinho):
    return utils.cart_total_qtd(carrinho)

@register.filter
def cart_totals(carrinho):
    return utils.cart_totals(carrinho)