# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import (
	GetDetectarSonido,LoginToken,LogoutToken,
	)
urlpatterns =[
	url(r'^detectar-cancion/', GetDetectarSonido.as_view(), name='detectar-sonido'),
	url(r'^login-token/', LoginToken, name='login-token'),
	url(r'^logout-token/', LogoutToken, name='logout-token'),
 	
]