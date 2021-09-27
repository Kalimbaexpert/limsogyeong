from django.shortcuts import render
import config as glb

# Create your views here.
def classes(request):
    context = {}
    return render(request, 'classes.html', context)

def detail(request):
    context = {}
    return render(request, 'detail.html', context)

def downld(request):
    if request.method == 'GET': 
        glb.server.SendFile("aa","bts.mp4")
    
    context= {}
    return render(request, 'detail.html', context)

def ctrl_left(request):
    if request.method == 'GET': 
        glb.server.SendMsg("aa","lft")
        print("left")
    
    context= {}
    return render(request, 'detail.html', context)

def ctrl_right(request):
    if request.method == 'GET': 
        glb.server.SendMsg("aa","rgt")
        print("right")
    
    context= {}
    return render(request, 'detail.html', context)