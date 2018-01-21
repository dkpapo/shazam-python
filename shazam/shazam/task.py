import os
import json
import sys
import warnings
from django.conf import settings
from celery import app
sys.path.append(settings.BASE_DIR)
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer
warnings.filterwarnings("ignore")


@app.task
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

	return song