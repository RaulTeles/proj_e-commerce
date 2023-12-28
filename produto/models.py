import os
from PIL import Image
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    #definindo onde a imagem vai ser armazenada
    imagem = models.ImageField(upload_to='produto_imagens/%Y/%M', blank=True, null=True)
    #passando que o slug tem que ser único
    slug = models.SlugField(unique=True, null=True, blank=True)
    preco_marketing = models.FloatField(verbose_name='Preço')
    preco_marketing_promocional = models.FloatField(default=0)
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variavel'),
            ('S', 'Simples'),
        )
    )

    def get_preco_formatado(self):
        return f'R$ {self.preco_marketing:.2f}'.replace('.',',')
    get_preco_formatado.short_description = 'Preço'

    #definindo um método para redimensionar as imagens
    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_width, original_height = img_pil.size
        if original_width <= new_width:
            img_pil.close()
            return  
        
        new_height = round((new_width * original_height) / original_width)

        new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)
        new_img.save(
            img_full_path,
            optimize=True,
            qulity=50
        )

    def save (self,*args, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.nome)}'
            self.slug = slug

        super().save(*args, **kwargs)

        max_image_size = 800

        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return self.nome



class Variacao(models.Model):
    nome = models.CharField(max_length=50, blank=True, null=True)
    Produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nome or self.Produto.nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'
