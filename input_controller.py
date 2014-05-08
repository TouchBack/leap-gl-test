from Leap import Vector

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math

class InputController(object):

	def __init__(self,callback=None):
		self.callback = callback

	def set_callback(self,callback):
		self.callback = callback

	def do_callback(self):
		if self.callback:
			self.callback(self.get_callback_params())
		else:
			print "=== No callback specified for InputController ==="

	def render(self):
		pass

	def update(self, fingers=None):
		pass

	def get_callback_params(self):
		return {}

	def get_feedback(self):
		return {}

	@staticmethod
	def get_inactive_feedback():
		return {'m': 0, 'n': 0, 'r': 0, 'g': 0, 'b': 0}

	def get_default_feedback(self):
		return InputController.get_inactive_feedback()

class XSlider(InputController):

	def __init__(self,center,radius,length,callback=None):
		super(XSlider,self).__init__(callback)
		self.center = center
		self.radius = radius
		self.length = length
		self.value = 0.5
		self.grabbed = False
		self.quadric = gluNewQuadric()
		self.touched = 0
		gluQuadricDrawStyle(self.quadric,GLU_LINE)

	def render(self):
		glPushMatrix()
		glTranslated(self.center.x-self.length/2.0,self.center.y,self.center.z)
		glRotated(90,0,1,0)
		color_r = 1.0-self.value
		color_g = self.value
		color_b = 0.5
		glColor3f(color_r,color_g,color_b)
		gluCylinder(self.quadric,self.radius,self.radius,self.length,16,8)
		glPopMatrix()

		glPushMatrix()
		pos = self.get_sphere_center()
		glTranslated(pos.x,pos.y,pos.z)
		glRotated(90,1,0,0)
		col = 0.9 if self.touched > 0 else 0.65
		glColor3f(col,col,col)
		glutWireSphere(self.get_sphere_radius(),16,16)
		glPopMatrix()

	def get_sphere_radius(self):
		return self.radius-1

	def get_sphere_center(self):
		return Vector(
			self.center.x-self.length/2.0 + (self.value*self.length),
			self.center.y,
			self.center.z)

	def slide_sphere(self,dist):
		old_value = self.value
		self.value += dist/self.length
		if self.value < 0.0:
			self.value = 0.0
		elif self.value > 1.0:
			self.value = 1.0
		if self.value != old_value:
			self.do_callback()

	def update(self,fingers=None):
		self.touched = 0
		if (not fingers) or len(fingers) < 1:
			return
		# else...
		for finger in fingers:
			center = self.get_sphere_center()
			radius = self.get_sphere_radius()
			# first decide whether it's touched
			if finger.tip_position.distance_to(center) <= radius + 20:
				self.touched += 1
			# then slide if necessary
			if finger.tip_position.distance_to(center) < radius:
				rel_to_sphere = finger.tip_position - center
				flattened = Vector(rel_to_sphere.x,0,rel_to_sphere.z)
				pitch_radians = flattened.angle_to(rel_to_sphere)
				radius_at_height = math.cos(pitch_radians)*radius
				# print "%f -> %f" % (math.degrees(pitch_radians),radius_at_height)
				z_dist = rel_to_sphere.z
				x_radius = math.sqrt(radius_at_height**2 - z_dist**2)
				x_dist = x_radius - math.fabs(rel_to_sphere.x)
				if finger.tip_position.x >= center.x:
					x_dist *= -1
				self.slide_sphere(x_dist)

	def get_callback_params(self):
		return {'value': self.value}

	def get_feedback(self):
		feedback = self.get_default_feedback()
		vibr = 100
		if self.touched > 0:
			feedback['m'] = vibr
			feedback['b'] = 100
			feedback['g'] = 100
		if self.touched > 1:
			feedback['n'] = vibr
		return feedback

class PopButton(InputController):

	SCALE_THRESHOLD = 0.5

	def __init__(self,center,radius,callback=None):
		super(PopButton,self).__init__(callback)
		self.center = center
		self.radius = radius
		self.scale = 1.0
		self.tween_scale = self.scale
		self.active = True
		self.contains_finger = False
		self.contained_count = 0

	def render(self):
		if self.active:
			if self.contains_finger:
				glColor3f(0.0,1.0,0.0)
			else:
				glColor3f(0.0,0.75,0.0)
			self.tween_scale = self.scale
		else:
			glColor3f(0.5,0.5,0.5)
			change = 0.1
			diff = self.scale - self.tween_scale
			if abs(diff) < change:
				self.tween_scale = self.scale
			else:
				self.tween_scale += math.copysign(change,diff)
		glPushMatrix()
		glTranslated(self.center.x,self.center.y,self.center.z)
		glRotated(90,1,0,0)
		glScaled(self.tween_scale,self.tween_scale,self.tween_scale)
		glutWireSphere(self.radius,40,40) # TODO solid/shaded
		glPopMatrix()

	def get_feedback(self):
		if not self.active or self.scale == 1.0:
			return self.get_default_feedback()
		else:
			vibr_scale = (self.scale - PopButton.SCALE_THRESHOLD)\
				/(1.0-PopButton.SCALE_THRESHOLD)
			vibr_val = 150-int(100*vibr_scale)
			ret = {'r':0,'g':vibr_val,'b':0,'m':vibr_val,'n':0}
			if self.contained_count > 1:
				ret['n'] = vibr_val
			return ret


	def update(self, fingers=None):
		if not fingers or len(fingers) == 0:
			self.scale = 1.0
			self.active = True
		else:
			sorted_fingers = sorted(fingers, \
				key=lambda finger: finger.tip_position.distance_to(self.center))
			closest_finger = sorted_fingers[0]
			target_radius = closest_finger.tip_position.distance_to(self.center)
			target_scale = target_radius / self.radius
			if target_scale > 1.0:
				target_scale = 1.0

			if self.active:
				self.scale = target_scale
				if self.scale <= PopButton.SCALE_THRESHOLD:
					self.scale = 1.0
					self.active = False
					self.do_callback()
			else:
				if target_scale == 1.0:
					self.active = True

			self.contains_finger = self.active and self.scale < 1.0

		self.contained_count = 0
		if self.active and fingers:
			for finger in fingers:
				if finger.tip_position.distance_to(self.center) <= self.scale * self.radius + 20:
					self.contained_count += 1

			# if self.active:
			# 	self.scale = target_scale
			# if self.scale >= 1.0:
			# 	self.scale = 1.0
			# 	self.active = True
			# elif self.active and self.scale <= PopButton.SCALE_THRESHOLD:
			# 	self.scale = 1.0
			# 	self.active = False
			# 	self.do_callback()
