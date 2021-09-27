import os

import cv2
import argparse
import chainer
import numpy as np
import timeit
import time

from media_reader import VideoReader, get_filename_without_extension
from pose_detector import PoseDetector, draw_person_pose
from logging import basicConfig, getLogger, DEBUG

#import cameras

chainer.using_config('enable_backprop', False)

if __name__ == '__main__':
    basicConfig(level=DEBUG)
    logger = getLogger(__name__)
    parser = argparse.ArgumentParser(description='Pose detector')
    #parser.add_argument('--video', type=str, default='', help='video file path')
    parser.add_argument('--gpu', '-g', type=int, default=-1, help='GPU ID (negative value indicates CPU)')
    args = parser.parse_args()

    #if args.video == '':
        #raise ValueError('Either --video has to be provided')

    chainer.config.enable_backprop = False
    chainer.config.train = False
   
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)

    # load model
    pose_detector = PoseDetector("posenet", "models/coco_posenet.npz", device=args.gpu)
    cnt = 0
    while True:

        
        ret, frame = cap.read()

        # algorithm starting point
        start_t = timeit.default_timer()
        
        if(cnt%3==0):
            poses, _ = pose_detector(frame)
            res_img = cv2.addWeighted(frame, 0.6, draw_person_pose(frame, poses), 0.4, 0)
            logger.debug("type: {}".format(type(poses)))
            logger.debug("shape: {}".format(poses.shape))
            logger.debug(poses)
            
        #algorithm terminating point
        terminate_t = timeit.default_timer()
        FPS = int(1./(terminate_t - start_t ))

        cv2.imshow('image',res_img)
        print(FPS)
        cnt = cnt + 1
        k = cv2.waitKey(30) & 0xff
        if k == 27: # Esc 키를 누르면 종료
            break
    
 