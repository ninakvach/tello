#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Massachusetts Institute of Technology

"""Extract images from a rosbag.
"""
import rospy
import os
import argparse
import time
import cv2
import sys
import rosbag
from std_msgs.msg import Header
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import csv
def main():
    #msg = Image()
    """Extract a folder of images from a rosbag.
    """
    parser = argparse.ArgumentParser(
        description="Extract images from a ROS bag.")
    parser.add_argument("bag_file", help="Input ROS bag.")
    parser.add_argument("output_dir", help="Output directory.")
    parser.add_argument("image_topic", help="Image topic.")

    args = parser.parse_args()

    print "Extract images from %s on topic %s into %s" % (args.bag_file, args.image_topic, args.output_dir)

    bag = rosbag.Bag(args.bag_file, "r")
    bridge = CvBridge()
    count = 0
    for topic, msg, t in bag.read_messages(topics=[args.image_topic]):
	#stamp = rospy.rostime.Time.from_sec(time.time())
	#msg.header.stamp=stamp
        print(msg.header.stamp)
        cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        cv2.imwrite(os.path.join(args.output_dir, "frame%06i.png" % count), cv_img)
        #print "Wrote image %i" % count

        count += 1

    return


if __name__ == '__main__':
    main()
