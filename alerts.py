import winsound as ws
from time import sleep
import os

#morse code SOS alert for when something happens
def sos_alert():
	if os.name == 'nt': #check if the system that this is running on is windows
		windows_alert()
	elif os.name = 'posix': #linux
		linux_alert()

# SOS morse code ==> later use stmp to send an email might be better if inactive or away
def windows_alert():
	ws.Beep(400, 200)
	sleep(0.1)
	ws.Beep(400, 200)
	sleep(0.1)
	ws.Beep(400, 200)
	sleep(0.5)
	ws.Beep(400, 200)
	sleep(0.5)
	ws.Beep(400, 200)
	sleep(0.5)
	ws.Beep(400, 200)
	sleep(0.5)
	ws.Beep(400, 200)
	sleep(0.1)
	ws.Beep(400, 200)
	sleep(0.1)
	ws.Beep(400, 200)
	sleep(0.5)

# not sure for now
def linux_alert():
	pass