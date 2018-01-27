#!/usr/bin/python

from evdev import UInput, ecodes, events, AbsInfo, util
import sys
import usb.core
import usb.util
import time

import bindings
import math
from config import LEFT_HANDED as LEFT_HANDED,\
	TRACKPAD_ENABLED as TRACKPAD_ENABLED, \
	PRESSURE_CURVE as PRESSURE_CURVE, \
	FULL_PRESSURE as FULL_PRESSURE

#tablet config values
PEN_MAX_X = 44000 #50800
PEN_MAX_Y = 27300 #31750 
PEN_MAX_Z = 2048 	#pressure

msc = 1
#specify capabilities for a virtual device
#one for each device:
#pen/pad, trackpad, and buttons
#note: I've chosen to include trackpad gestures with the buttons based on how they're reported over USB

#pressure sensitive pen tablet area with 2 stylus buttons and no eraser
cap_pen = {
	ecodes.EV_KEY: [ecodes.BTN_TOUCH, ecodes.BTN_TOOL_PEN],
	ecodes.EV_ABS: [
		(ecodes.ABS_X, AbsInfo(0,0,PEN_MAX_X,0,0,5080)), #value, min, max, fuzz, flat, resolution
		(ecodes.ABS_Y, AbsInfo(0,0,PEN_MAX_Y,0,0,5080)),
		(ecodes.ABS_PRESSURE, AbsInfo(0,0,PEN_MAX_Z,0,0,0)),],
	ecodes.EV_MSC: [ecodes.MSC_SCAN], #not sure why, but it appears to be needed
	}


#buttons must be defined in the same sequential order as in the Linux specs
#https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
cap_btn = {
	ecodes.EV_KEY: [ecodes.KEY_MINUS,ecodes.KEY_EQUAL,ecodes.KEY_E, 
					ecodes.KEY_LEFTBRACE,ecodes.KEY_RIGHTBRACE,
					ecodes.KEY_LEFTCTRL, ecodes.KEY_S, ecodes.KEY_LEFTSHIFT, ecodes.KEY_Z,
					ecodes.KEY_LEFTALT, ecodes.KEY_SPACE,
					ecodes.KEY_UP, ecodes.KEY_LEFT, ecodes.KEY_RIGHT, ecodes.KEY_DOWN, 
					ecodes.BTN_MOUSE, ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE]
	}

# create our 2 virtual devices
vpen = UInput(cap_pen, name="pinspiroy950-pen", version=0x3)
vbtn = UInput(cap_btn, name="pinspiroy950-button", version=0x5)

time.sleep(0.1) # needed due to some xserver feature 

# input specific functions
def id_btn(data):
	if LEFT_HANDED:
		btn_switch_LH[data[4]](vbtn)
	else:
		btn_switch[data[4]](vbtn)
	


def pressure_curve(z):
	z = z/FULL_PRESSURE
	if z > PEN_MAX_Z:
		z = PEN_MAX_Z
	if PRESSURE_CURVE == 'LINEAR':
		pass
	elif PRESSURE_CURVE == 'HARD':
		z = z*z/PEN_MAX_Z
	elif PRESSURE_CURVE == 'SOFT':
		z = z*math.sqrt(z)/math.sqrt(PEN_MAX_Z)
	return math.floor(z)
global cntr
cntr = 0

#handler for pen input
def id_pen(data):
	x = data[3]*255 + data[2]
	y = data[5]*255 + data[4]
	z = data[7]*255 + data[6]
	if PRESSURE_CURVE:
		z = pressure_curve(z)
	#rotate coordinates if left handed
	if LEFT_HANDED:
		x = PEN_MAX_X-x
		y = PEN_MAX_Y-y

	#print(str(x) + ', ' + str(y) + '; ' + str(z))
	#vpen.write(ecodes.EV_MSC,ecodes.MSC_SCAN,msc) # this seems to be necessary, value is arbitrary

	vpen.write(ecodes.EV_ABS, ecodes.ABS_X, x)
	vpen.write(ecodes.EV_ABS, ecodes.ABS_Y, y)
	vpen.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, z)

	if data[1] == 128: # pen registered, but not touching pad
		vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 0)
	elif (data[1] == 130 or data[1] == 131) and cntr > 100: # stylus button 
		bindings.styl1(vbtn)
		global cntr
		cntr = 0
		#if z>10:
		#	vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 1)
		#else:
		#	vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 0)
		#vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS, 1)
	elif (data[1] == 132 or data[1] == 133) and cntr > 100: # stylus button 2
		bindings.styl2(vbtn)
		global cntr
		cntr = 0
		#if z>10:
		#	vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 1)
		#else:
		#	vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 0)
		#vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS2, 1)
	elif data[1] == 129: # == 129; pen touching pad
		vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 1)

	vpen.write(ecodes.EV_KEY, ecodes.BTN_TOOL_PEN, 1)

	vpen.syn() #sync all inputs together

	bindings.styl0(vbtn)



# switch to handle input types
input_switch = {
	224:id_btn, #buttonpad 
	129:id_pen, #stylus down
	128:id_pen, #stylus up
	130:id_pen, #stylus button 1
	131:id_pen, #stylus button 1 (while toutching)
	132:id_pen, #stylus button 2
	133:id_pen  #stylus button 2 (while touching)
}

# switch to handle button types
btn_switch = {
	1  :bindings.btn1, #from top to bottom
	2  :bindings.btn2, 
	4  :bindings.btn3, 
	8  :bindings.btn4, 
	16 :bindings.btn5, 
	32 :bindings.btn6, 
	64 :bindings.btn7,
	128:bindings.btn8,

	0 :bindings.btn0, #button released
}

# reverse button order for LH setting
btn_switch_LH = {
	128:bindings.btn1, #clockwise from top left
	64 :bindings.btn2, 
	32 :bindings.btn3, 
	16 :bindings.btn4, 
	8  :bindings.btn5, 
	4  :bindings.btn6, 
	2  :bindings.btn7,
	1  :bindings.btn8,
 

	0 :bindings.btn0, #button released
}




# get unidentified huion USB device
# boilerplate USB data reading from pyusb library
dev = usb.core.find(idVendor=0x256c, idProduct=0x006e)
interface = 0
endpoint = dev[0][(0,0)][0]
if dev.is_kernel_driver_active(interface) is True:
	dev.detach_kernel_driver(interface)
	usb.util.claim_interface(dev, interface)
	print('interface 0 grabbed')
interface = 1
if dev.is_kernel_driver_active(interface) is True:
	dev.detach_kernel_driver(interface)
	usb.util.claim_interface(dev, interface)
	print('interface 1 grabbed')
##msc = 1
print('pinspiroy driver should be running!')
while True:
	cntr +=1
	try:
		##msc+=1
		# data received as array of [0,255] ints
		data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
		input_switch[data[1]](data)
	except usb.core.USBError as e:
		data = None
		if e.args == ('Operation timed out',):
				continue
usb.util.release_interface(dev, interface)
dev.attach_kernel_driver(interface)
