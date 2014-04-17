from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import Leap
from Leap import *

from time import sleep

window = 0                                             # glut window number
width, height = 800, 600                               # window size
x,y = 0,0
leap = None

r = 1.0
g = 0.0
b = 0.0

def draw_rect(x, y, width, height):
	glBegin(GL_QUADS)                                  # start drawing a rectangle
	glVertex2f(x, y)                                   # bottom left point
	glVertex2f(x + width, y)                           # bottom right point
	glVertex2f(x + width, y + height)                  # top right point
	glVertex2f(x, y + height)                          # top left point
	glEnd()    

def refresh2d(width, height):
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(0.0, width, 0.0, height, 0.0, 1.0)
	glMatrixMode (GL_MODELVIEW)
	glLoadIdentity()

def map_range(num, min1, max1, min2, max2, clamp=True):
	percent = (num-min1)/(max1-min1)
	if clamp:
		percent = 0 if percent < 0 else percent
		percent = 1 if percent > 1 else percent
	return min2 + (max2-min2)*percent

def draw():                                            # ondraw is called all the time
	global leap, width, height, r, g, b
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
	glLoadIdentity()                                   # reset position
	refresh2d(width, height)                           # set mode to 2d

	frame = leap.frame()

	# if len(frame.fingers) > 0:
	# 	x = frame.fingers[0].tip_position.x
	# else:
	# 	x = 0
		
	


	#print "Getting gestures"
	for gesture in frame.gestures():
		#print "GESTURE"
		if gesture.type == Leap.Gesture.TYPE_SWIPE:
			swipe = SwipeGesture(gesture)
			if swipe.state == Leap.Gesture.STATE_STOP:
				old_r = r
				old_g = g
				old_b = b
				r = old_b
				g = old_r
				b = old_g
				#print "Red: %f -> %f" % (old_r, r)


	for finger in frame.fingers:
		f_x = map_range(finger.tip_position.x, -255,255, 0, width, False)
		f_y = map_range(finger.tip_position.y, 0,512, 0, height, False)
		z_mult = map_range(finger.tip_position.z, -255, 255, 1.0, 0.0)
		glColor3f(r*z_mult,g*z_mult,b*z_mult) # set color
		draw_rect(f_x, f_y, 10, 10) # draw rect

	
	glutSwapBuffers()
	
def gl_init():
	global leap
	# init leap first!!!
	leap = Leap.Controller()
	leap.enable_gesture(Leap.Gesture.TYPE_SWIPE);
	# initialization
	glutInit()                                             # initialize glut
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	glutInitWindowSize(width, height)                      # set window size
	glutInitWindowPosition(0, 0)                           # set window position
	window = glutCreateWindow("noobtuts.com")              # create window with title
	glutDisplayFunc(draw)                                  # set draw function callback
	glutIdleFunc(draw)                                     # draw all the time
	glutMainLoop()                                         # start everything

gl_init()