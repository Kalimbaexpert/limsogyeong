from django.urls import path

from.import views

app_name = 'administration' 

urlpatterns = [
	# ex: /polls/
	path('', views.my_page, name='my_page'),
	path('camera', views.camera, name='camera'),
	path('ctrl_left', views.ctrl_left, name='ctrl_left'),
	path('ctrl_right', views.ctrl_right, name='ctrl_right')
]