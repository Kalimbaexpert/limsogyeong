from django.urls import path

from.import views

app_name = 'upload' 

urlpatterns = [
	# ex: /polls/
	path('', views.upload, name='upload')
	# path('pose', views.poseprogram, name='success')
]