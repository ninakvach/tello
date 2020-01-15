#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Point,Quaternion
import threading
import socket
import numpy
import cv2
rospy.init_node("tello_node_tracker")

host = ''
port = 7000
locaddr = (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)
sock.bind(locaddr)

def shutdown_work():
    global sock
    print("closing socket...")
    sock.close()
    print("socket closed...")

rospy.on_shutdown(shutdown_work)

def no(dummy):
  pass

speed_pub = rospy.Publisher("RC", Quaternion, queue_size=1)
rc = Quaternion()
cv2.namedWindow("speed",cv2.WINDOW_NORMAL)
cv2.createTrackbar("speed_factor", "speed", 75, 100, no)
cv2.createTrackbar("desired_radius", "speed", 150, 300, no)
center_of_frame_x = 480
center_of_frame_y = 360
max_x_error = center_of_frame_x
max_y_error = center_of_frame_y
min_radius = 0
max_radius = 300
radius_range = max_radius - min_radius
def callback(data):
  cv2.imshow("speed",0)
  cv2.waitKey(1)
  speed_factor = cv2.getTrackbarPos("speed_factor", "speed")
  desired_radius = cv2.getTrackbarPos("desired_radius","speed")
  if data.z > 20:
    center_of_shape_x = data.x
    center_of_shape_y = data.y
    radius_of_shape = data.z
    print("radius of shape : {}".format(radius_of_shape))
    x_error = center_of_frame_x - center_of_shape_x
    y_error = center_of_frame_y - center_of_shape_y
    d_error =   desired_radius - radius_of_shape
    norm_x_error = float(x_error) / float(max_x_error)
    norm_y_error = float(y_error) / float(max_y_error)
    norm_d_error = (float(d_error) - float(min_radius))/ float(radius_range)
    a = int((norm_x_error * speed_factor) / 2) * (-1)
    rc.x = a
    b = int(norm_d_error * speed_factor) 
    rc.y = b
    c = int(norm_y_error * speed_factor)
    rc.z = c
    d = a
    rc.w = d    
    command = "rc" + " " + str(a) + " " + str(b)+ " " +str(c) + " " + str(d)
    try:
      command = command.encode(encoding="utf-8")
      _ = sock.sendto(command, tello_address)
      speed_pub.publish(rc)
      print("a: " + str(a) + " b: " + str(b) +" c: " + str(c) + " d: " + str(d))
    except Exception:
      print("error while sending {}".format(command))

rospy.Subscriber("track",Point,callback,queue_size=1)

try:
  rospy.spin()
except rospy.ROSInterruptException:
  print("interrupt")