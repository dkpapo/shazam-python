# -*- encoding: utf-8 -*-
import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import warnings
from django.conf import settings
from celery import app
sys.path.append(settings.BASE_DIR)
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer
warnings.filterwarnings("ignore")
from pyfcm import FCMNotification
from django.contrib.auth.models import User
from api.models import (TokensFCM)
from rest_framework.authtoken.models import Token

@app.task()
def detectar_sonido(nombre_archivo):
    
	# load config from a JSON file (or anything outputting a python dictionary)
	with open(settings.BASE_DIR+"/dejavu.cnf.SAMPLE") as f:
		config = json.load(f)


	djv = Dejavu(config)

	# # Fingerprint all the mp3's in the directory we give it
	# djv.fingerprint_directory("mp3", [".mp3"])

	# Recognize audio from a file
	song = djv.recognize(FileRecognizer, settings.BASE_DIR+"/archivos_reconocer/"+nombre_archivo+".mp3")
	print "From file we recognized: %s\n" % song


	####una vez detectado hay que eliminar el archivo
	archivo=settings.BASE_DIR+"/archivos_reconocer/"+nombre_archivo+".mp3"
	os.remove(archivo)

	##debo notificar al afiliado sobre su nueva cancion por medio de una notificacion push
	push_service = FCMNotification(api_key=settings.FCM_APIKEY)
	token, datos = nombre_archivo.split('_')

	try:
		usuario=Token.objects.get(key=token)

		usuario_token=TokensFCM.objects.get(usuario=usuario.user)
		
		registration_id = usuario_token.token
		message_title = "Nueva canción detectada"
		message_body = "Hola "+usuario.user.username+" la canción que estabas escuchando es "+song['song_name']
		result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)


	except Token.DoesNotExist:
		pass
	except TokensFCM.DoesNotExist:
		pass

	

	return song