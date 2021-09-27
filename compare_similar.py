import os
import cv2
import argparse
import chainer
import numpy as np
import time
import timeit
import math
import subprocess
import shlex
import datetime
import pandas as pd

from media_reader import VideoReader, get_filename_without_extension
from pose_detector import PoseDetector, draw_person_pose
from logging import basicConfig, getLogger, DEBUG
#####################################################
def normalization(x, y):
    denominator = math.sqrt(x**2+y**2)
    if denominator == 0:
        x = 0 
        y = 0
    else:
        x = x/denominator
        y = y/denominator
    
    return x, y

def similarity_cal(p1, p2, scores):
    p1_L2Norm = []
    p2_L2Norm = []
    sum_p1Confidence = 0
    summation2 = 0
    #p1_L2Norm = np.linalg.norm(p1[-1,:,:2],axis=1,ord=2)
    #p2_L2Norm = np.linalg.norm(p2[-1,:,:2],axis=1,ord=2)

    print(p1)
    print(p2)
    print(scores)
    
    for i in range(0,18):
        x, y = normalization(p1[i,0], p1[i,1])
        p1_L2Norm.append(x)
        p1_L2Norm.append(y)
        x, y = normalization(p2[i,0], p2[i,1])
        p2_L2Norm.append(x)
        p2_L2Norm.append(y)
        sum_p1Confidence_temp = scores[i]
        sum_p1Confidence = sum_p1Confidence + sum_p1Confidence_temp

    if sum_p1Confidence == 0:
        summation1 = 0
    else:
        summation1 = 1/sum_p1Confidence

    for i in range(0,35):
        tempConf = math.floor(i/2)
        summation2_temp = scores[tempConf] * abs(p1_L2Norm[i]-p2_L2Norm[i])
        summation2 = summation2 + summation2_temp

    similarity = summation1 * summation2
    similarity = (1-similarity)*100
    return similarity
######################################################################################

def SimilarCompare () :
    # initial value
    data_teacher = pd.read_csv("sample_teacher.csv")
    data_student = pd.read_csv("sample_student.csv")
    start = 0
    div = 18
    sum_smr = 0
    len_data_teacher = (len(data_teacher)+1)/19
    len_data_student = (len(data_student)+1)/19
    min_len = min(len_data_teacher, len_data_teacher)
    print("min_length : ")
    print(min_len)
    num_frame = min_len
    while min_len:
        out_teacher = data_teacher[start:start+div]
        poses_teacher = out_teacher.values
        out_student = data_student[start:start+div]
        poses_student = out_student.values
        start = start + 19
        
        similarity = similarity_cal(poses_teacher[:,:2], poses_student[:,:2], poses_student[:,2])
        sum_smr = sum_smr + similarity
        print(similarity)
        min_len -= 1

    print("-------------Done!-------------")
        
    avr_smr = sum_smr / num_frame
    print(avr_smr)
    
    
    return avr_smr

