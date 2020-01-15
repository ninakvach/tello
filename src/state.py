#!/usr/bin/env python
from __future__ import print_function
import rospy
import threading
import socket
import time
from std_msgs.msg import String

rospy.init_node("tello_node_state")

state_pub = rospy.Publisher("state", String,queue_size=1)

def shutdown_work():
    global sock
    print("closing socket...")
    sock.close()
    print("socket closed...")

rospy.on_shutdown(shutdown_work)

host = '0.0.0.0'
port = 8890
locaddr = (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(locaddr)

while not rospy.is_shutdown():
      try:
            data, _ = sock.recvfrom(1518)
      except Exception:
            print("Error receiving state info")
            continue
      else:
            data = data.decode(encoding="utf-8")
            rospy.loginfo(data)
            state_pub.publish(data)
