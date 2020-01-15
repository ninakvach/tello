#!/usr/bin/env python
import rospy
import threading
import socket
import time
from sensor_msgs.msg import Joy
from geometry_msgs.msg import QuaternionStamped
rospy.init_node("tello_node_command")

host = ''
port = 9000
locaddr = (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)
sock.bind(locaddr)

joy_rc = rospy.Publisher("joy_to_rc",QuaternionStamped,queue_size=1)

qts = QuaternionStamped()

def shutdown_work():
    global sock
    print("closing socket...")
    sock.close()
    print("socket closed...")

rospy.on_shutdown(shutdown_work)

def joy_callback(joy_mgs):
    if joy_mgs.buttons[9] == 1:
        command = "takeoff"
    elif joy_mgs.buttons[8] == 1:
        command = "land"
    elif int(joy_mgs.axes[5]) == 1:
        command = "flip f"
    elif int(joy_mgs.axes[5]) == -1:
        command = "flip b"
    elif int(joy_mgs.axes[4]) == 1:
        command = "flip l"
    elif int(joy_mgs.axes[4]) == -1:
        command = "flip r"
    else:
        a = int(-100 * joy_mgs.axes[0])
        b = int(+100 * joy_mgs.axes[1])
        c = int(+100 * joy_mgs.axes[3])
        d = int(-100 * joy_mgs.axes[2])
        qts.quaternion.x = a
        qts.quaternion.y = b
        qts.quaternion.z = c
        qts.quaternion.w = d
        
        command = "rc" + " " + str(a) + " " + str(b) + " " + str(c) + " " + str(d)
        print(command)
    try:
        command = command.encode(encoding="utf-8")
        _ = sock.sendto(command, tello_address)
        joy_rc.publish(qts)
    except Exception:
        print("error while sending {}".format(command))

joy_sub = rospy.Subscriber("/joy",Joy,joy_callback, queue_size=1)
command = None
receive_event = threading.Event()
receive_event.set()

class receive(threading.Thread):
    def run(self):
        while receive_event.is_set():
            try:
                data, _ = sock.recvfrom(1518)
                print(data.decode(encoding="utf-8"))
            except Exception:
                print("Error receiving response to given command")
        receive_event.clear()

print("starting receive thread")
receive_thread = receive()
receive_thread.daemon = True
receive_thread.start()

keep_open_event = threading.Event()
keep_open_event.set()
def keep_open():
    global sock
    global tello_address
    com = 'command'
    com = com.encode(encoding="utf-8")
    while keep_open_event.is_set():
        try:
            _ = sock.sendto(com, tello_address)
        except Exception:
            print("error while sending {}".format(com))
        #print("sent: {}".format(com))
        time.sleep(5)
keep_open_thread = threading.Thread(target=keep_open)
keep_open_thread.daemon = True

command = "command"
try:
    print("entering command mode")
    command = command.encode(encoding="utf-8")
    sent = sock.sendto(command, tello_address)
except Exception:
    print("error while sending {}".format(command))
keep_open_thread.start()
print("started keep_open thread")
while not rospy.is_shutdown():
    receive_event.wait()
    try:
        command = raw_input()
    except EOFError:
        continue
    
    if not command:
        print("battery?")
        command = "battery?"
    if "end" in command:
        print("ending")
        keep_open_event.clear()
        keep_open_thread.join()
        break
    try:
        command = command.encode(encoding="utf-8")
        sent = sock.sendto(command, tello_address)
    except Exception:
        print("error while sending {}".format(command))
    receive_event.set()