from django.shortcuts import render
from .models import Video
from .forms import VideoForm
from django.http import Http404
from video_pose_detector import *

def upload(request):

    lastvideo= Video.objects.last() 

    videofile= lastvideo.videofile if lastvideo else None


    form= VideoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        video = form.save(commit=False)
        video.author = request.user  # 추가한 속성 author 적용
        video.save()
        #form = VideoForm()
        #context= {'videofile': videofile, 'form': form}
        print(video.videofile.name)
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(type(video.videofile.name))
        file_name = video.videofile.name
        PoseEstimate(file_name)
        form = VideoForm()
        context= {'videofile': videofile, 'form': form}

        return render(request, 'upload.html', context)
    else:
        form = VideoForm()
        context= {'videofile': videofile, 'form': form}

    return render(request, 'upload.html', context)

# def poseprogram(request):
#     try:
#         os.system("pwd")
#         os.system("ls")
#         os.system("python3 video_pose_detector.py --video path")

#     except Question.DoesNotExist:

#         raise Http404("Question does not exist")
    
#     return render(request,'success.html')