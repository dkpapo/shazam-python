# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class TokensFCM(models.Model):
    """Modelo para manejar los municipios destino de la plataforma

        Atributos(modelo):
            codigo: identificador único del municipio
            nombre: nombre del municipio
            departamento: llave foránea del departamento
            latitud: latitud del municipio
            longitud: longitud del municipio
    """
    fecha_token= models.DateField(('Fecha compra'),auto_now_add=True)
    token       =  models.TextField(('Token'))
    usuario = models.OneToOneField(User, related_name='usuario_token')

    class Meta:
        """metadato de clase

            verbose_name: devuelve el nombre singular del modelo
            verbose_name_plural: devuelve el nombre plural del modelo
        """
        verbose_name        = "Token firebase usuario"
        verbose_name_plural = "Tokens usuario"

    def __unicode__(self):
        """
            retorno nombre
        """
        return "%s" % (self.usuario.username)  