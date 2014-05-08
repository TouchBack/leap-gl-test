#!/usr/bin/env python

from Leap import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from math import degrees

WIN_W = 800
WIN_H = 600
WIN_TITLE = "3D test"

GL_FOV = 60

leap = None
cubes = []

def init():
	glClearColor(0.0, 0.0, 0.2, 1.0)
	glClearDepth(1.0)
	glEnable(GL_DEPTH_TEST)
	glDepthFunc(GL_LEQUAL)
	glShadeModel(GL_SMOOTH)
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


#TODO gluLookAt :)
def draw():
	global cubes, leap

	# first logic
	del cubes[:]

	frame_ct = 10
	min_frame_ct = 5

	fingers = []
	finger_ids = []
	for i in range (0,frame_ct):
		for finger in leap.frame(i).fingers:
			fingers.append(finger)
			if finger.id not in finger_ids:
				finger_ids.append(finger.id)

	valid_ids = []
	for fid in finger_ids:
		instances = filter(lambda f: f.id == fid, fingers) # get matching ids
		if len(instances) >= min_frame_ct:
			pos_list = map(lambda f: f.tip_position, instances) # extract pos vectors
			dir_list = map(lambda f: f.direction, instances) # extract pos vectors
			total_pos = reduce(lambda v1,v2: v1 + v2, pos_list) # add all vector components
			total_dir = reduce(lambda v1,v2: v1 + v2, dir_list) # add all vector components

			use_median = False

			x_list = sorted(map(lambda p: p.x, pos_list))
			y_list = sorted(map(lambda p: p.y, pos_list))
			z_list = sorted(map(lambda p: p.z, pos_list))
			p_list = sorted(map(lambda d: d.pitch, dir_list))
			y_list = sorted(map(lambda d: d.yaw, dir_list))

			x = 0
			y = 0
			z = 0
			pitch = 0
			yaw = 0
			l = len(instances)

			if use_median:
				mid = int(l/2)
				x = x_list[mid]
				y = y_list[mid]
				z = z_list[mid]
				pitch = p_list[mid]
				yaw = y_list[mid]
			else:
				x = total_pos.x/l
				y = total_pos.y/l
				z = total_pos.z/l
				pitch = (total_dir/l).pitch
				yaw = (total_dir/l).yaw



			cubes.append({
				'x': x,
				'y': y,
				'z': z,
				'pitch': pitch,
				'yaw': yaw
			})


	# then draw
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)

	glPushMatrix()
	scl = 1.0/500.0
	glScaled(scl,scl,scl)


	total_yaw = 0.0
	for cube in cubes:
		total_yaw += cube['yaw']

	avg_yaw = total_yaw / float(len(cubes)) if len(cubes) != 0 else 0

	glRotated( degrees(avg_yaw)/10 ,0,-1,0)
	glRotated(20,1,0,0)
	glTranslated(0,-500,-500)


	glColor3f(0.75,0.75,0.75)
	
	glPushMatrix()


	radius = 175
	glTranslated(0,radius*1.5,0)

	glRotated(90,1,0,0)

	glutWireSphere(radius,40,40)
	#glutWireTeapot(radius) # <- lol :D

	glPopMatrix()


	for cube in cubes:
		glPushMatrix()
		#glTranslated(1.5, 0.0, -7.0)
		glTranslated(cube['x'],cube['y'],cube['z'])
		glRotated( degrees(cube['yaw']), 0, -1, 0 )
		glRotated( degrees(cube['pitch']), 1, 0, 0 )
		cube_scl = 10.0
		glScaled(cube_scl,cube_scl,cube_scl)

		# translate back so tip is actually at tip
		glTranslated(0,0,1)
		glScaled(0.5,0.5,2)

		glBegin(GL_QUADS)                # Begin drawing the color cube with 6 quads
		# Top face (y = 1.0)
		# Define vertices in counter-clockwise (CCW) order with normal pointing out
		glColor3f(0.0, .75, 0.0)     # Green
		glVertex3f( 1.0, 1.0, -1.0)
		glVertex3f(-1.0, 1.0, -1.0)
		glVertex3f(-1.0, 1.0,  1.0)
		glVertex3f( 1.0, 1.0,  1.0)

		# Bottom face (y = -1.0)
		glColor3f(0.75, 0.5*0.75, 0.0)     # Orange
		glVertex3f( 1.0, -1.0,  1.0)
		glVertex3f(-1.0, -1.0,  1.0)
		glVertex3f(-1.0, -1.0, -1.0)
		glVertex3f( 1.0, -1.0, -1.0)

		# Front face  (z = 1.0)
		glColor3f(0.75, 0.0, 0.0)     # Red
		glVertex3f( 1.0,  1.0, 1.0)
		glVertex3f(-1.0,  1.0, 1.0)
		glVertex3f(-1.0, -1.0, 1.0)
		glVertex3f( 1.0, -1.0, 1.0)

		# Back face (z = -1.0)
		glColor3f(0.75, 0.75, 0.0)     # Yellow
		glVertex3f( 1.0, -1.0, -1.0)
		glVertex3f(-1.0, -1.0, -1.0)
		glVertex3f(-1.0,  1.0, -1.0)
		glVertex3f( 1.0,  1.0, -1.0)

		# Left face (x = -1.0)
		glColor3f(0.0, 0.0, 0.75)     # Blue
		glVertex3f(-1.0,  1.0,  1.0)
		glVertex3f(-1.0,  1.0, -1.0)
		glVertex3f(-1.0, -1.0, -1.0)
		glVertex3f(-1.0, -1.0,  1.0)

		# Right face (x = 1.0)
		glColor3f(0.75, 0.0, 0.75)     # Magenta
		glVertex3f(1.0,  1.0, -1.0)
		glVertex3f(1.0,  1.0,  1.0)
		glVertex3f(1.0, -1.0,  1.0)
		glVertex3f(1.0, -1.0, -1.0)

		glEnd()  # End of drawing color-cube
		glPopMatrix()

	#glColor3f(0.0,0.5,0.5)
	#glTranslated(-2.0,0,0)
	#glutSolidSphere(1.0,20,20)

	glPopMatrix()
	glutSwapBuffers()

def resize(w,h):
	global WIN_H, WIN_W
	if w < 1: w = 1
	if h < 1: h = 1
	WIN_W = w
	WIN_H = h

	aspect = float(WIN_W)/float(WIN_H)

	glViewport(0,0,WIN_W,WIN_H)

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(GL_FOV, aspect, 0.1, 1000)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()


def main():
	global leap
	print "Hello 3D!"
	leap = Controller()
	glutInit()
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	glutInitWindowSize(WIN_W,WIN_H)
	glutCreateWindow(WIN_TITLE)
	glutDisplayFunc(draw)
	glutReshapeFunc(resize)
	glutIdleFunc(draw)
	init()
	glutMainLoop()
	print "Bye 3D!"

### Utils ###

def map_range(num, min1, max1, min2, max2, clamp=True):
	percent = (num-min1)/(max1-min1)
	if clamp:
		percent = 0 if percent < 0 else percent
		percent = 1 if percent > 1 else percent
	return min2 + (max2-min2)*percent

### Run ###
if __name__ == "__main__":
	main()