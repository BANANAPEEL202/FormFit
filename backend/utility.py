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

#@title Mediapipe Method
##runs media pipe on the video
def extractSkeleton(filePath: str, half: bool = True):
  start_time = time.time()
  mp_drawing = mp.solutions.drawing_utils
  mp_pose = mp.solutions.pose

  pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

  cap = cv2.VideoCapture(filePath)
  print("FPS CHECK: " + str(cap.get(cv2.CAP_PROP_FPS)))

  if cap.isOpened() == False:
      print("Error opening video stream or file")
      raise TypeError

  frame_width = int(cap.get(3))
  frame_height = int(cap.get(4))


  frameNum = 0
  results = [];
  while cap.isOpened():
      ret, image = cap.read()
      if not ret:
          break

      image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
      image.flags.writeable = False
      result = pose.process(image, )
      results.append(result)


      #image.flags.writeable = True
      #image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      #mp_drawing.draw_landmarks(
      #    image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

      frameNum +=1
      #print(frameNum)
  pose.close()
  cap.release()
  print("Mediapipe Finished in " + str(np.round(time.time() - start_time, 2)) + "s")
  start_time = time.time()

  ##Parse mediapipe output
  keypoints = []
  for frame in results:
    result = frame.pose_landmarks.landmark
    frameKeypoints = []
    landmarks = []
    for data_point in result:
      landmarks.append({
          'x': data_point.x,
          'y': data_point.y,
          'z': data_point.z,
          'Visibility': data_point.visibility,
          })

    #head
    index = 0;
    frameKeypoints.append(landmarks[index]['x'])
    frameKeypoints.append(landmarks[index]['y'])

    #arms
    if (not half):
      #left arm (might need to verify)
      for index in [12, 14, 16]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #right arm
      for index in [11, 13, 15]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])
    elif (landmarks[12]['z'] < landmarks[11]['z']):
      for index in [12, 14, 16]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])
      for index in [12, 14, 16]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])
    else:
      #right arm
      for index in [11, 13, 15]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])
      for index in [11, 13, 15]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])



    if (not half):
      #left leg
      for index in [24, 26, 28]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #left foot
      for index in [30, 32]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #right leg
      for index in [23, 25, 27]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #right foot
      for index in [29, 31]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])
    elif (landmarks[24]['z'] < landmarks[23]['z']):
      #left leg
      for index in [24, 26, 28]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #left foot
      for index in [30, 32]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #left leg
      for index in [24, 26, 28]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #left foot
      for index in [30, 32]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])
    else:
      #right leg
      for index in [23, 25, 27]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #right foot
      for index in [29, 31]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])
      #right leg
      for index in [23, 25, 27]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

      #right foot
      for index in [29, 31]:
        frameKeypoints.append(landmarks[index]['x'])
        frameKeypoints.append(landmarks[index]['y'])

    #midpoints
    frameKeypoints.append((landmarks[11]['x']+landmarks[12]['x'])/2)
    frameKeypoints.append((landmarks[11]['y']+landmarks[12]['y'])/2)
    frameKeypoints.append((landmarks[24]['x']+landmarks[23]['x'])/2)
    frameKeypoints.append((landmarks[24]['y']+landmarks[23]['y'])/2)
    keypoints.append(frameKeypoints)

  np.save(filePath + '.npy', np.array(keypoints))
  print("Mediapipe Parsed in " + str(np.round(time.time() - start_time, 2)) + "s")

#@title Extract Stats Methods

def dot(vA, vB):
    return vA[0]*vB[0]+vA[1]*vB[1]

@dispatch(int, int, int, np.ndarray, int, int)
def angle(landmark1, landmark2, landmark3, keypoint, width, height):
    # Get nicer vector form
    x1 = int(width-keypoint[landmark1*2]*width)
    y1 = int(keypoint[landmark1*2+1]*height)
    x2 = int(width-keypoint[landmark2*2]*width)
    y2 = int(keypoint[landmark2*2+1]*height)
    x3 = int(width-keypoint[landmark3*2]*width)
    y3 = int(keypoint[landmark3*2+1]*height)
    vA = [(x2-x1), (y2-y1)]
    vB = [(x2-x3), (y2-y3)]
    # Get dot prod
    dot_prod = dot(vA, vB)
    # Get magnitudes
    magA = dot(vA, vA)**0.5
    magB = dot(vB, vB)**0.5
    # Get cosine value
    cos_ = dot_prod/magA/magB
    # Get angle in radians and then convert to degrees
    angle = math.acos(dot_prod/magB/magA)
    # Basically doing angle <- angle mod 360
    ang_deg = math.degrees(angle)%360

    if ang_deg-180>=0:
        # As in if statement
        return 360 - ang_deg
    else:
        return ang_deg


@dispatch(int, int, int, int, np.ndarray, int, int)
def angle(landmark1, landmark2, landmark3, landmark4, keypoint, width, height):
    # Get nicer vector form
    x1 = int(width-keypoint[landmark1*2]*width)
    y1 = int(keypoint[landmark1*2+1]*height)
    x2 = int(width-keypoint[landmark2*2]*width)
    y2 = int(keypoint[landmark2*2+1]*height)
    x3 = int(width-keypoint[landmark3*2]*width)
    y3 = int(keypoint[landmark3*2+1]*height)
    x4 = int(width-keypoint[landmark4*2]*width)
    y4 = int(keypoint[landmark4*2+1]*height)
    vA = [(x2-x1), (y2-y1)]
    vB = [(x4-x3), (y4-y3)]
    # Get dot prod
    dot_prod = dot(vA, vB)
    # Get magnitudes
    magA = dot(vA, vA)**0.5
    magB = dot(vB, vB)**0.5
    # Get cosine value
    cos_ = dot_prod/magA/magB
    # Get angle in radians and then convert to degrees
    angle = math.acos(dot_prod/magB/magA)
    # Basically doing angle <- angle mod 360
    ang_deg = math.degrees(angle)%360

    if ang_deg-180>=0:
        # As in if statement
        return 360 - ang_deg
    else:
        return ang_deg


def angleHorizontal(landmark1, landmark2, keypoint, width, height):
    # Get nicer vector form
    x1 = int(width-keypoint[landmark1*2]*width)
    y1 = int(keypoint[landmark1*2+1]*height)
    x2 = int(width-keypoint[landmark2*2]*width)
    y2 = int(keypoint[landmark2*2+1]*height)
    x3 = 0
    y3 = 0
    x4 = 1
    y4 = 0
    vA = [(x2-x1), (y2-y1)]
    vB = [(x4-x3), (y4-y3)]
    # Get dot prod
    dot_prod = dot(vA, vB)
    # Get magnitudes
    magA = dot(vA, vA)**0.5
    magB = dot(vB, vB)**0.5
    # Get cosine value
    cos_ = dot_prod/magA/magB
    # Get angle in radians and then convert to degrees
    angle = math.acos(dot_prod/magB/magA)
    # Basically doing angle <- angle mod 360
    ang_deg = math.degrees(angle)%360

    if ang_deg-180>=0:
        # As in if statement
        return 360 - ang_deg
    else:
        return ang_deg

def getDist(landmark1, landmark2, keypoint, width, height):
    x1 = int(width-keypoint[landmark1*2]*width)
    y1 = int(keypoint[landmark1*2+1]*height)
    x2 = int(width-keypoint[landmark2*2]*width)
    y2 = int(keypoint[landmark2*2+1]*height)
    return ((x2-x1)**2 + (y2-y1)**2)**(1/2)

def drawLetter(landmark1, keypoint, text, angle, dist, frame, width, height):
    x1 = int(width-keypoint[landmark1*2]*width)
    y1 = int(keypoint[landmark1*2+1]*height)
    a = - math.radians(angle)
    x2 = int(x1+math.cos(a)*dist)
    y2 = int(y1+math.sin(a)*dist)
    cv2.putText(frame, text, (x2, y2),  cv2.FONT_HERSHEY_DUPLEX, 1.2, (207, 115, 27), 2, cv2.LINE_AA)

def getX(landmark, keypoint, width, height):
  return int(width - keypoint[landmark*2]*width)

def drawLine(landmark1, landmark2, frame, keypoint, color, height, width, radius, thickness, cv2):
      x1 = int(width-keypoint[landmark1*2]*width)
      y1 = int(keypoint[landmark1*2+1]*height)
      x2 = int(width-keypoint[landmark2*2]*width)
      y2 = int(keypoint[landmark2*2+1]*height)
      cv2.line(frame, (x1, y1), (x2, y2), color, thickness)
      cv2.circle(frame, (x1, y1), radius, color, -1)
      cv2.circle(frame, (x2, y2), radius, color, -1)

def getDist(landmark1, landmark2, keypoint, width, height):
      x1 = int(width-keypoint[landmark1*2]*width)
      y1 = int(keypoint[landmark1*2+1]*height)
      x2 = int(width-keypoint[landmark2*2]*width)
      y2 = int(keypoint[landmark2*2+1]*height)
      return ((x2-x1)**2 + (y2-y1)**2)**(1/2)
