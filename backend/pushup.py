# -*- coding: utf-8 -*-
"""Mediapipe Main.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DLukXrQguRqrCG55mUoHostywApsmG2C
"""

# from google.colab import drive
# drive.mount('/content/drive')

## dowloads media pipe
# !pip install -q mediapipe==0.10.0
import os
import cv2
import mediapipe as mp
import numpy as np
import sys
import cv2
import math
from multipledispatch import dispatch
import matplotlib.pyplot as plt
import time

from utility import extractSkeleton, drawLine, drawLetter, angle, getDist, getX



def getStatsPushUp(vidPath, userPath, AIPath):
  start_time = time.time()
  drawAngles = False

  cap = cv2.VideoCapture(vidPath)
  ret, frame = cap.read()
  frameNum = 0
  height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  fps = round(cap.get(cv2.CAP_PROP_FPS))
  if (drawAngles):
    videoOutput = cv2.VideoWriter("Stats 2.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

  keypoints = np.load(userPath)
  AIkeypoints = np.load(AIPath)

  font = cv2.FONT_HERSHEY_TRIPLEX
  fontScale = 1.5

  skipFrames = 0
  frameNum = skipFrames

  userMinKneeAngle = 190
  userMinBackAngle = 190
  userMinElbowAngle = 190

  minFrame = 0;

  if (ret == False):
    print("NO VIDEO FILE FOUND")
  while (ret):
      keypoint = keypoints[frameNum]
      if (frameNum-skipFrames < len(AIkeypoints)):
          AIkeypoint = AIkeypoints[frameNum-skipFrames]
      else:
          AIkeypoint = AIkeypoints[len(AIkeypoints)-1]

      if (frameNum % 3 == 0 or frameNum == skipFrames):

          if (angle(1, 2, 3, keypoint, width, height) < userMinElbowAngle):
            minFrame = frameNum

          userMinKneeAngle = min(userMinKneeAngle, angle(7, 8, 9, keypoint, width, height))
          userMinBackAngle = min(userMinBackAngle, angle(1, 7, 8, keypoint, width, height))
          userMinElbowAngle = min(userMinElbowAngle, angle(1, 2, 3, keypoint, width, height))

      if (drawAngles):
        dist = 40
        drawLetter(8, keypoint, str(np.round(angle(1, 7, 8, keypoint, width, height), 1)), 0, dist, frame, width, height)
        drawLetter(7, keypoint, str(np.round(angle(7, 8, 9, keypoint, width, height), 1)), 0, dist, frame, width, height)
        videoOutput.write(frame)
      plt.close()
      ret, frame = cap.read()
      frameNum+=1



      #print(frameNum)

  if (drawAngles):
    videoOutput.release()
  cap.release()

  plt.close()
  #print(userMinKneeAngle)
  #print(userMinBackAngle)
  #print(AIMinKneeAngle)
  #print(AIMinBackAngle)
  #print(minFrame)
  #minknee = heal to butt angle
  #minback = knee to shoulder angle
  #minshoulder = butt to head angle
  print("Stats Extracted in " + str(np.round(time.time() - start_time, 2)) + "s")
  return userMinKneeAngle, userMinBackAngle, userMinElbowAngle, minFrame

def backAngleComparison(userAngle: float):
  feedback = {
    "name": "Hip Angle",
    "feedback": "",
    "satisfactory": False
  }
  if userAngle - 165 > 15:
    feedback["feedback"] = "You're doing great! For proper form, make sure you raise your hip!"
  elif userAngle - 165 < -15:
    feedback["feedback"] = "You're doing great! For proper form, make sure you lower your hip!"
  else:
    feedback["feedback"] = "Your form is perfect! Keep it up!"
    feedback["satisfactory"] = True
  return feedback

# returns True is form is correct
def kneeAngleComparison(userAngle: float):
  feedback = {
    "name": "Knee Angle",
    "feedback": "",
    "satisfactory": False
  }
  if abs(userAngle - 156) > 15:
    feedback["feedback"] = "Keep it up! For proper form, make sure to keep your legs straight!"
  else:
    feedback["feedback"] = "Your form is perfect! Keep it up!"
    feedback["satisfactory"] = True
  return feedback

# returns True is form is correct
def elbowAngleComparison(userAngle: float):
  feedback = {
    "name": "Elbow Angle",
    "feedback": "",
    "satisfactory": False
  }
  if abs(userAngle - 75) > 15:
    feedback["feedback"] = "You're doing amazing! For proper form, make sure to bend your arms at 90 degrees!"
  else:
    feedback["feedback"] = "Your form is perfect! Keep it up!"
    feedback["satisfactory"] = True
  return feedback



def calcFormPushUp(userMinKneeAngle, userMinBackAngle, userMinElbowAngle):
  backAngle = backAngleComparison(userMinBackAngle)
  kneeAngle = kneeAngleComparison(userMinKneeAngle)
  elbowAngle = elbowAngleComparison(userMinElbowAngle)
  print("Form Analyser Finished")
  return [backAngle, kneeAngle, elbowAngle]

#@title Visualizer Method

def visualizePushUp(formVid, customerForm, AIForm, minFrame, outputPath):
    start_time = time.time()
    keypoints = np.load(customerForm)
    AIkeypoints = np.load(AIForm)

    cap = cv2.VideoCapture(formVid)
    ret, frame = cap.read()
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    output = cv2.VideoWriter(outputPath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    print(f"Opened: {output.isOpened()}")

    ret, frame = cap.read()
    frameNum = 0
    thickness = 8
    radius = 10
    blue = (207, 115, 27)
    red = (102, 66, 238)

    if (ret == False):
      print("NO VID FOUND")

    offset = int(abs(len(AIkeypoints)/2 - minFrame))+3#220
    while (ret):
        #scale and shift AI keypoints
        keypoint = keypoints[frameNum]
        AIkeypoint = AIkeypoints[frameNum + offset]
        if (frameNum == 0):
          dist1 = getDist(1, 9, keypoint, width, height)
          dist2 = getDist(1, 9, AIkeypoint, width, height)
          scale = dist1/dist2 #scale calculated based on fencer's spine
        yOffset = AIkeypoint[9*2+1]*scale - keypoint[9*2+1]
        xOffset = AIkeypoint[9*2]*scale - keypoint[9*2]
        AIkeypoint[0::2] = [x*scale - xOffset for x in AIkeypoint[0::2]]
        AIkeypoint[1::2] = [y*scale - yOffset for y in AIkeypoint[1::2]]

        overlay = frame.copy()
        #right arm 
        drawLine(1, 2, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(2, 3, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        #left arm 
        drawLine(4, 5, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(5, 6, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        #left leg 
        drawLine(7, 8, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(8, 9, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(9, 10, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(9, 11, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(10, 11, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        #right leg 
        drawLine(12, 13, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(13, 14, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(14, 15, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(14, 16, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(15, 16, overlay, keypoint, blue, height, width, radius, thickness, cv2)

        #drawLine(17, 18, frame, keypoint, blue, height, width, radius, thickness, cv2)
        #drawLine(17, 0 , frame, keypoint, blue, height, width, radius, thickness, cv2)
        #drawLine(1, 4 , frame, keypoint, blue, height, width, radius, thickness, cv2)
        #drawLine(7, 12   , frame, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(7, 1, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(0, 1, overlay, keypoint, blue, height, width, radius, thickness, cv2)
        drawLine(4, 12, overlay, keypoint, blue, height, width, radius, thickness, cv2)



        #draw AI
        #right arm 
        drawLine(1, 2, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(2, 3, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        #left arm 
        drawLine(4, 5, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(5, 6, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        #left leg
        drawLine(7, 8, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(8, 9, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(9, 10, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(9, 11, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(10, 11, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        #right leg 
        drawLine(12, 13, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(13, 14, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(14, 15, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(14, 16, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(15, 16, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)

        #drawLine(17, 18, frame, AIkeypoint, red, height, width, radius, thickness, cv2)
        #drawLine(17, 0, frame, AIkeypoint, red, height, width, radius, thickness, cv2)
        #drawLine(1, 4, frame, AIkeypoint, red, height, width, radius, thickness, cv2)
        #drawLine(7, 12, frame, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(7, 1, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(0, 1, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)
        drawLine(4, 12, overlay, AIkeypoint, red, height, width, radius, thickness, cv2)


        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        output.write(frame)
        ret, frame = cap.read()
        frameNum+=1
        #print(frameNum)

    # Caller closes file
    # output.release()
    cap.release()
    print("Visualizer finished in " + str(np.round(time.time() - start_time, 2)) + "s")

#global variables
inputPath = "minAtEnd"
rootPath = "/content/drive/MyDrive/Hacklytics/"
AI_PATH = "./Exemplar Squat 1.npy"
outputPath = "./Output.mp4"
half = False

#Code
if __name__ == "__main__":
  extractSkeleton(inputPath)
  print("get stats")
  values = getStatsSquat(inputPath, inputPath + ".npy", AI_PATH)
  feedback = calcFormSquat(values[0], values[1], values[2], values[3], values[4], values[5])
  minFrameNum = values[6]
  visualizeSquat(inputPath, inputPath + ".npy", AI_PATH, minFrameNum, outputPath)