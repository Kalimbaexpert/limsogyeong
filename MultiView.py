import cv2
import mediapipe as mp
import time
import os
from logging import basicConfig, getLogger, DEBUG
#import poses
import numpy as np
from ffpyplayer.player import MediaPlayer

def MultiView(downloadingFileName):
  print("start")
  mp_drawing = mp.solutions.drawing_utils
  mp_pose = mp.solutions.pose

  basicConfig(level=DEBUG)
  logger = getLogger(__name__)

  # For webcam input:
  cap = cv2.VideoCapture(0)
  cap2 = cv2.VideoCapture("./clientVideos/"+downloadingFileName)
  mp_holistic = mp.solutions.holistic
  player = MediaPlayer("./clientVideos/"+downloadingFileName)
  fps = cap.get(cv2.CAP_PROP_FPS)
  fourcc = cv2.VideoWriter_fourcc(*'MP4V')
  out = cv2.VideoWriter('./clientVideos/output.mp4', fourcc, fps, (640, 480))
  #cap.set(3,960)
  #cap.set(4,720)
  #cap = cv2.VideoCapture("1.mp4")
  #For Video input:
  prevTime = 0
  with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1) as pose:
    while cap.isOpened():
      success, image = cap.read()
      success2, image2 = cap2.read()
      audio_frame, val = player.get_frame()
      if not success or not success2:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        break
      image2 = cv2.resize(image2,(640,480),fx=0,fy=0, interpolation = cv2.INTER_CUBIC) # video resize

      # Convert the BGR image to RGB.
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      #image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False
      results = pose.process(image)
      #image2.flags.writeable = False
      #results2 = pose.process(image2)

      # Draw the pose annotation on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      #image2.flags.writeable = True
      #image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
      #mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS) 

      currTime = time.time()
      fps = 1 / (currTime - prevTime)
      prevTime = currTime
      
      #coordinates = poses.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS) 
      logger.debug(results)
      #coordinates2 = poses.draw_landmarks(image2, results2.pose_landmarks, mp_pose.POSE_CONNECTIONS) 
      #logger.debug(results2)

      image = cv2.flip(image, 1)
      #cv2.putText(image, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 2)
      #cv2.imshow('BlazePose', image)

      # concatanate image Horizontally
      Hori = np.concatenate((image2, image), axis=1)
        
      # concatanate image Vertically
      #Verti = np.concatenate((image, image2), axis=0)

      out.write(image)
      cv2.imshow('HORIZONTAL', Hori)
      #cv2.imshow('VERTICAL', Verti)
      if val != 'eof' and audio_frame is not None:
        #audio
        img, t = audio_frame

      if cv2.waitKey(5) & 0xFF == 27:
        break

  out.release()
  cap.release()
  cap2.release()
  cv2.destroyAllWindows()
  print("end")