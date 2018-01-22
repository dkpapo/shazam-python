# -*- encoding: utf-8 -*-
import json
from datetime import datetime
from django.views.generic import  View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from django.http import (HttpResponse, HttpResponseRedirect,JsonResponse)
from rest_framework.authentication import (SessionAuthentication, BasicAuthentication, 
	TokenAuthentication)
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from pydub import AudioSegment
from django.conf import settings
from shazam.task import detectar_sonido
from models import (TokensFCM)




class GetDetectarSonido(View):
	"""docstring for GetDetectarSonido"""
	# authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
	# permission_classes = (IsAuthenticated,)
	
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(GetDetectarSonido, self).dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		"""
		Defino las variables con las cuales voy a enviarselas al template para reenderizar luego las graficas
		"""
		try:

			print(request.FILES)

			token = request.POST['token']
			audio = request.FILES['audio']

			token   = Token.objects.get(key=token)
			usuario = token.user


			song = AudioSegment.from_file(audio, format="mp3")
			nombre_archivo=str(token)+"_"+str(datetime.now())
			song.export(settings.BASE_DIR+"/archivos_reconocer/"+nombre_archivo+".mp3", format="mp3")

			###mandamos a celery para que busque la cancion
			resultado = detectar_sonido.delay(nombre_archivo)
			
			data = ([{"detail":"Información para procesar almacenada correctamente."}])
			data = json.dumps(data)
			response = HttpResponse(data, content_type="application/json", status=200)
			return response
			

		except MultiValueDictKeyError:

			data = ([{"detail":"Por favor complete los campos"}])
			data = json.dumps(data)
			response = HttpResponse(data, content_type="application/json", status=400)
			return response
		except Token.DoesNotExist:

			data = ([{"detail":"No se encuentra autenticado,por favor inicie sesión"}])
			data = json.dumps(data)
			response = HttpResponse(data, content_type="application/json", status=400)
			return response



@csrf_exempt
def LoginToken(request):

	if request.method == 'POST':
		try:
			
			username    = request.POST['usuario']
			password    = request.POST['contrasena']
			#password    = b64decode(password)
			registrationId = request.POST.get('registrationId', None)

			try:
				user  = User.objects.get(username=username)
				check = check_password(password, user.password)

			except User.DoesNotExist:
				user = False
			
			if user is not False and check == True:
				if user.is_active == True:
					###guardar el token para el usuario en la tabla de fcm

					token    = Token.objects.get_or_create(user=user)
					fcm_user=TokensFCM(
						token=registrationId,
						usuario=user
					)

					fcm_user.save()
					data     = ([{"detail":"Has iniciado sesión correctamente."}])
					data     = json.dumps(data)
					response = HttpResponse(data, content_type="application/json", status=200)
					response['Authorization'] =  str(token)
					return response
				else:
					data        = ([{"detail":"Su cuenta se encuentra inhabilitada por el administrador por esta razón no puedes iniciar sesión"}])
					data        = json.dumps(data)
					response    = HttpResponse(data, content_type="application/json", status=405)
					response['WWW-Authenticate'] = 'Token'
					return response            
			else:
				data     = ([{"detail":"Usuario y/o contraseña incorrectas."}])
				data     = json.dumps(data)
				response = HttpResponse(data, content_type="application/json" ,status=401)
				response['WWW-Authenticate'] = 'Token'
				return response
		except MultiValueDictKeyError:

			data = ([{"detail":"Por favor complete los campos"}])
			data = json.dumps(data)
			response = HttpResponse(data, content_type="application/json", status=400)
			return response
	else:
		data        = ([{"detail":"Método no permitido."}])
		data        = json.dumps(data)
		response    = HttpResponse(data, content_type="application/json", status=405)
		return response

@csrf_exempt
def LogoutToken(request):
	"""
	Api para cerrar sesión de un usuario

	@return json

	@method POST
	"""
	if request.method == "POST":
		try:
			token   = request.POST['token']
			token   = Token.objects.get(key=token)
			token.delete()
			fcm_user=TokensFCM.objects.get(usuario=token.user)
			fcm_user.delete()

			data     = ([{"detail":"Sesión finalizada correctamente."}])
			data     = json.dumps(data)
			response = HttpResponse(data, content_type="application/json", status=200)
			return response
		except Token.DoesNotExist:
			data     = ([{"detail":"El usuario no existe, por favor verifique la información."}])
			data     = json.dumps(data)
			response = HttpResponse(data, content_type="application/json", status=400)
			return response
		except TokensFCM.DoesNotExist:
			data     = ([{"detail":"El usuario no existe, por favor verifique la información."}])
			data     = json.dumps(data)
			response = HttpResponse(data, content_type="application/json", status=400)
			return response
		except MultiValueDictKeyError:
			data     = ([{"detail":"Algo ha ocurrido mal, por favor reinicie la aplicación"}])
			data     = json.dumps(data)
			response = HttpResponse(data, content_type="application/json", status=400)
			return response
	else:
		data     = ([{"detail":"Método no permitido."}])
		data     = json.dumps(data)
		response = HttpResponse(data, content_type="application/json", status=405)
		return response