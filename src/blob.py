#!/usr/bin/env python
import rospy
import cv2
import time
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Point
import imutils
rospy.init_node("tello_node_blob")

def no(dummy):
   pass

pos_pub = rospy.Publisher("track",Point,queue_size=1)
cap = None
bridge = CvBridge()
p = Point()
cv2.namedWindow("tracking")
cv2.createTrackbar('lower_hue', 'tracking', 0, 60, no)
cv2.createTrackbar('upper_hue', 'tracking', 10, 60, no)
cv2.createTrackbar('lower_sat', 'tracking', 200, 255, no)
cv2.createTrackbar('upper_sat', 'tracking', 255, 255, no)
cv2.createTrackbar('lower_val', 'tracking', 80, 255, no)
cv2.createTrackbar('upper_val', 'tracking', 200, 255, no)
cv2.createTrackbar('font_size', 'tracking', 50, 100, no)

def callback(data):
  global cap
  global bridge
  lh = cv2.getTrackbarPos("lower_hue", "tracking")
  uh = cv2.getTrackbarPos("upper_hue", "tracking")
  ls = cv2.getTrackbarPos("lower_sat", "tracking")
  us = cv2.getTrackbarPos("upper_sat", "tracking")
  lv = cv2.getTrackbarPos("lower_val", "tracking")
  uv = cv2.getTrackbarPos("upper_val", "tracking")
  fs = cv2.getTrackbarPos("font_size", "tracking")
  lower_red = np.array([lh, ls, lv])
  upper_red = np.array([uh, us, uv])
  try:
    cap = bridge.imgmsg_to_cv2(data, "bgr8")
  except CvBridgeError as e:
    print(e)
  try:
    (width, height, _) = cap.shape
    center_of_frame = (int(height / 2), int(width / 2))
    hsv = cv2.cvtColor(cap, cv2.COLOR_BGR2HSV)
  except Exception as e:
    print(e)
  else:
    mask = cv2.inRange(hsv, lower_red, upper_red)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    if len(cnts) > 0:
      c = max(cnts, key=cv2.contourArea)
      ((x, y), radius) = cv2.minEnclosingCircle(c)
      p.x, p.y, p.z = x, y,radius
      if radius > 20:
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        pos_pub.publish(p)
        cv2.circle(cap, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        cv2.circle(cap, center, 5, (0, 0, 255), -1)
        cv2.putText(cap, str(center), center, cv2.FONT_HERSHEY_SIMPLEX, float(fs)/float(100), (0, 255, 0), 1, cv2.LINE_8)
        cv2.circle(cap, center_of_frame, 5, (0, 0, 255), -1)
        cv2.putText(cap, str(center_of_frame), center_of_frame, cv2.FONT_HERSHEY_SIMPLEX, float(fs)/float(100), (0, 255, 0), 1, cv2.LINE_8)
        cv2.line(cap, center_of_frame, center, (255, 0, 0), 2)


    res = cv2.bitwise_and(cap, cap, mask=mask)
    cv2.imshow('frame2',cap)
    cv2.imshow("res", res)   
    cv2.waitKey(1)

image_sub = rospy.Subscriber("image_topic",Image,callback,queue_size=1)

try:
  rospy.spin()
except rospy.ROSInterruptException:
  print("interrupt")
finally:
  cv2.destroyAllWindows()  
