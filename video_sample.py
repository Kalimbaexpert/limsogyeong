import os
import cv2
import numpy as np
import time
import timeit
import math
import subprocess
import shlex
import datetime

KEY_DICT = {
    27: 'ESC',
    119: 'W',
    115: 'S',
    120: 'X'
}

cap = cv2.VideoCapture("cover.mp4")

delay = 30
timer = 0
prev_time = 0
FPS = 120

while True:
    keycode = cv2.waitKey(1) & 0xff
    timer += 1

    if keycode in [27, 119, 115]:
        if keycode == 27: # Esc 키를 누르면 종료
            print('Press: {}, Determinate'.format(KEY_DICT[keycode]))
            break
        elif keycode == ord('w'):
            delay = delay - 30 
            if delay <= 0: 
                delay = 30
        elif keycode == ord('s'):
            delay += 30
        print('Press: {}, delay: {} mms'.format(KEY_DICT[keycode],delay))

    elif timer >= delay:
        current_time = time.time() - prev_time
        ret, frame = cap.read()
        if current_time > 1./ FPS:
            prev_time = time.time()
            cv2.imshow("video", frame)
            timer = 0
    
    elif keycode == ord('x'):
        start1, start2 = input("start : ").split()
        end1, end2 = input("end : ").split()
        command = "ffmpeg -i cover.mp4 -ss 00:"+start1+":"+start2+" -to 00:"+end1+":"+end2+" -c copy output.mp4"
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
        for line in process.stdout:
            now = datetime.datetime.now()
            print(now, line)
        print("-------------Done!-------------")
        
cv2.destroyAllWindows()
        

 
