from django.shortcuts import render
import config as glb

# Create your views here.

def my_page(request):
    context = {}
    return render(request, 'my_page.html', context)

def camera(request):
    context = {}
    return render(request, 'camera.html', context)

def ctrl_left(request):
    if request.method == 'GET': 
        #send tcpip
        glb.server.SendMsg("aa","lft")
    
    context= {}
    return render(request, 'camera.html', context)

def ctrl_right(request):
    if request.method == 'GET': 
        #send tcpip
        glb.server.SendMsg("aa","rgt")
    
    context= {}
    return render(request, 'camera.html', context)