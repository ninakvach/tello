#!/usr/bin/env python
from __future__ import print_function
import rospy
import cv2
import threading
import socket
import time
import sys
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import os

rospy.init_node("tello_node_video")
host = ''
port = 8000
locaddr = (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)
sock.bind(locaddr)
cap = None
image_pub = rospy.Publisher("image_topic",Image,queue_size=1)
signal = threading.Event()
signal.set()
def receive():
    frame = None
    bridge = CvBridge()
    global cap
    global image_pub
    cap = cv2.VideoCapture("udp://@0.0.0.0:11111")
    if not cap.isOpened():
        print("VideoCapture not opened")
    else:
        while signal.is_set():
            _, frame = cap.read()
            #cv2.imshow("frame", frame)
            #cv2.waitKey(1)
            try:
                stamp = rospy.rostime.Time.from_sec(time.time())
                image = bridge.cv2_to_imgmsg(frame, "bgr8")
                image.header.stamp= stamp
                image_pub.publish(image)
            except CvBridgeError as e:
                print(e)
                break
            
receive_thread = threading.Thread(target=receive)
receive_thread.daemon = True

def main():
    command = "command"
    streamon = False
    in_command_mode = False
    wait_time = 3
    try:
        command = command.encode(encoding="utf-8")
        _ = sock.sendto(command,tello_address)
    except Exception:
        print('!ERROR! sending "{}" failed'.format(command))
    else:
        in_command_mode = True
        print("in_command_mode : {}".format( in_command_mode))

    if not in_command_mode:
        print("could not enter command mode...")
    else:
        command = "streamon"
        while not streamon:
            try:
                command = command.encode(encoding="utf-8")
                _ = sock.sendto(command,tello_address)
            except Exception:
                print('!ERROR! sending "{}" failed'.format(command))
            else:
                streamon = True
            if not streamon:
                print("waiting 3 seconds before trying again")
                time.sleep(wait_time)
        print("streaming started")
        receive_thread.start()
        rospy.spin()

try:
    main()
except rospy.ROSInterruptException:
    pass
finally:
    signal.clear()
    print("waiting for receive_thread to join")
    receive_thread.join()
    print("joined")
    cv2.destroyAllWindows()
    print("closing socket...")
    sock.close()
    print("socket closed...")