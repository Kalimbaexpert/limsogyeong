from django.urls import path

from.import views

app_name = 'classes' 

urlpatterns = [
	# ex: /polls/
	path('', views.classes, name='classes'),
	path('detail', views.detail, name='detail'),
	path('downld', views.downld, name='downld'),
	path('ctrl_left', views.ctrl_left, name='ctrl_left'),
	path('ctrl_right', views.ctrl_right, name='ctrl_right')
]