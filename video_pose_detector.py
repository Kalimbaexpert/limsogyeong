import os
import cv2
# import argparse
import chainer
import numpy as np
import time
import timeit
import math
import pandas as pd
import csv

from media_reader import VideoReader, get_filename_without_extension
from pose_detector import PoseDetector, draw_person_pose
from logging import basicConfig, getLogger, DEBUG
import os.path




chainer.using_config('enable_backprop', False)

def PoseEstimate(filename) :
    csv_path = 'sample_teacher.csv'
    
    if os.path.isfile(csv_path):
        os.remove('sample_teacher.csv')

    basicConfig(level=DEBUG)
    logger = getLogger(__name__)
    # parser = argparse.ArgumentParser(description='Pose detector')
    # parser.add_argument('--video', type=str, default='', help='video file path')
    # parser.add_argument('--gpu', '-g', type=int, default=-1, help='GPU ID (negative value indicates CPU)')
    # args = parser.parse_args()

    #if args.video == '':
        #raise ValueError('Either --video has to be provided')

    chainer.config.enable_backprop = False
    chainer.config.train = False
   
    cap = cv2.VideoCapture(filename)

    # load model
    pose_detector = PoseDetector("posenet", "models/coco_posenet.npz", device=0)
    
    # initial delay
    delay = 0

    while True:
        ret, frame = cap.read()
        # frame = cv2.resize(frame,(640,480),fx=0,fy=0, interpolation = cv2.INTER_CUBIC) # video resize
        poses, scores, scorec_list = pose_detector(frame)
        res_img = cv2.addWeighted(frame, 0.6, draw_person_pose(frame, poses), 0.4, 0)

        logger.debug("type: {}".format(type(poses)))
        logger.debug("shape: {}".format(poses.shape))
        logger.debug(poses)

        p1_deep_num = []
        p1_person_num = int(len(poses))
        while p1_person_num:
            p1_deep_num.append(p1_person_num)
            p1_person_num -= 1
            p1_deep_num.sort()

        points = range(0,18)

        #for p1_i in p1_deep_num:
            #print("p1_person : {}".format(p1_i))
            #for p1_j in points:
                #print("{} : {}".format(p1_j, poses[p1_i-1,p1_j,:2]))
            #print("--------------------------------")

        df = pd.DataFrame(poses[0,:,:2])
        df['2'] = scorec_list[:18]

        df.to_csv('sample_teacher.csv', mode ='a', index=False)

        # cv2.imshow("chainer", res_img)

        k = cv2.waitKey(30) & 0xff
        if k == 27: # Esc 키를 누르면 종료
            break
    cv2.destroyAllWindows()