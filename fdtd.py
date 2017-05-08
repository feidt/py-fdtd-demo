from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import numpy as np

class Grid(object):
	def __init__(self,dim):
		self.cdtds = 1.0 / np.sqrt(2.0)
		self.vac_imp = 377.0
		self.height = dim
		self.width = dim
		self.Ez = np.zeros((dim*dim),dtype=float)
		self.Hx = np.zeros((dim*dim),dtype=float)
		self.Hy = np.zeros((dim*dim),dtype=float)
		self.fHxH = np.zeros((dim*dim),dtype=float)
		self.fHxE = np.zeros((dim*dim),dtype=float)
		self.fHyH = np.zeros((dim*dim),dtype=float)
		self.fHyE = np.zeros((dim*dim),dtype=float)
		self.fEzH = np.zeros((dim*dim),dtype=float)
		self.fEzE = np.zeros((dim*dim),dtype=float)

	def init(self):
		for y in range(self.height):
			for x in range(self.width):
				i = y + self.height*x
				self.Ez[i] = 0.0
				self.Hx[i] = 0.0
				self.Hy[i] = 0.0
				self.fHxH[i] = 1.0
				self.fHxE[i] = self.cdtds/self.vac_imp;
				self.fHyH[i] = 1.0
				self.fHyE[i] = self.cdtds/self.vac_imp;
				self.fEzH[i] = self.cdtds*self.vac_imp;
				self.fEzE[i] = 1.0

	def update(self,time):
		"""
		update all field values by Yee's algorithm
		"""
		for x in range(self.width):
			for y in range(self.height-1):
				i = y + x*self.height
				self.Hx[i] = self.Hx[i]*self.fHxH[i] - (self.Ez[i + 1] - self.Ez[i])*self.fHxE[i]

		for x in range(self.width-1):
			for y in range(self.height):
				i = y + x*self.height
				self.Hy[i] = self.Hy[i]*self.fHyH[i] + (self.Ez[i + self.height] - self.Ez[i])*self.fHyE[i]

		for x in range(1,self.width-1):
			for y in range(1,self.height-1):
				i = y + x*self.height
				self.Ez[i] = self.Ez[i]*self.fEzE[i] + (self.Hy[i] - self.Hy[i-self.height] - self.Hx[i] + self.Hx[i-1])*self.fEzH[i]

		#wavelength, k-vector and frequency
		lamb = 400.
		k_vector = 2 * 3.141 / lamb;
		omega = k_vector;

		# add an oscillating point source
		self.Ez[10 + self.height * 30] += 4000.*np.sin(omega*time)*np.exp(-0.002*time)


class Colormap(object):
	def __init__(self):
		"""
		add a MATLAB Jet like colormap
		"""
		self.palette = np.zeros(255*3,dtype=int)
		self.colors = np.array([0, 0, 127,
		                       0, 0, 255,
		                       0, 127, 255,
		                       0, 255, 255,
		                       127, 255, 127,
		                       255, 255, 0,
		                       255, 127, 0,
		                       255, 0, 0,
		                       127, 0, 0,
		                       255, 255, 255])

	def init(self):
		for c in range(9):
			for i in range(25):
				weight_c0 = (25.0 - i)/25.0
				weight_c1 = i/25.0

				# interpolate between the base colors
				self.palette[c * 3 * 25 + 3 * i] = int((self.colors[c*3] * weight_c0  + self.colors[(c+1)*3] * weight_c1))
				self.palette[c * 3 * 25 + 3 * i + 1] = int((self.colors[c*3 + 1] * weight_c0 + self.colors[(c+1)*3+1] * weight_c1))
				self.palette[c * 3 * 25 + 3 * i + 2] = int((self.colors[c*3 + 2] * weight_c0 + self.colors[(c+1)*3 +2] * weight_c1))


class Simulation(object):
	def __init__(self):
		self.time = 0.
		self.grid = Grid(70)
		self.colormap = Colormap()
		self.render_3d = False

	def init(self,width, height):
	    glClearColor(1.0, 1.0, 1.0, 0.0)
	    glClearDepth(1.0)
	    glDepthFunc(GL_LESS)
	    glEnable(GL_DEPTH_TEST)
	    glShadeModel(GL_SMOOTH)

	    glMatrixMode(GL_PROJECTION)
	    glLoadIdentity()
	    gluPerspective(45., float(width)/float(height), 0.1, 100.0)

	    glMatrixMode(GL_MODELVIEW)

	def resize(self,width, height):
	    if height == 0:
		    height = 1

	    glViewport(0, 0, width, height)
	    glMatrixMode(GL_PROJECTION)
	    glLoadIdentity()
	    gluPerspective(45.0, float(width)/float(height), 0.1, 150.0)
	    glMatrixMode(GL_MODELVIEW)


	def render(self):
		"""
		renders the field value Ez as a false color rectangle
		"""
		red = 0.
		green = 0.
		blue = 0.

		# pixel width
		pw = 1.
		ph = 1.

		# grid scaling factor
		scale_factor=1.

		#define how long the point source will oscillate and update the simulation time
		if self.time < 1000:
			self.time += 10.

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()


		if self.render_3d == True:
			glTranslatef(-self.grid.width/2.,-self.grid.height/10.,-120.0)
			glRotatef(100,1,0,0)
		else:
			glTranslatef(-self.grid.width/2.,-self.grid.height/2.,-100.0)

		# run thru the grid and plot the Ez
		for x in range(self.grid.width):
			for y in range(self.grid.height):
				intensity = np.abs(self.grid.Ez[x + self.grid.height*y])
				if intensity >=0. and intensity < 215:
					red = self.colormap.palette[int(intensity)*3]
					green = self.colormap.palette[int(intensity)*3+1]
					blue = self.colormap.palette[int(intensity)*3+2]
				else:
					red = 255.
					green = 255.
					blue = 255.

				sc_int = -intensity/40.
				# draw a rectangle for every field value

				if self.render_3d == True:

					# top
					glBegin(GL_QUADS);
					glColor3f(red/255.,green/255.,blue/255.)
					glVertex3f(scale_factor*x,scale_factor*y,-1+sc_int)
					glVertex3f(scale_factor*x,scale_factor*(y-ph),-1+sc_int)
					glVertex3f(scale_factor*(x+pw),scale_factor*(y-ph),-1+sc_int)
					glVertex3f(scale_factor*(x+pw),scale_factor*y,-1+sc_int)
					glEnd()

					# bottom
					glBegin(GL_QUADS);
					glColor3f(red/255.,green/255.,blue/255.)
					glVertex3f(scale_factor*x,scale_factor*y,-1)
					glVertex3f(scale_factor*x,scale_factor*(y-ph),-1)
					glVertex3f(scale_factor*(x+pw),scale_factor*(y-ph),-1)
					glVertex3f(scale_factor*(x+pw),scale_factor*y,-1)
					glEnd()


					# back
					glBegin(GL_QUADS);
					glColor3f(red/255.,green/255.,blue/255.)
					glVertex3f(scale_factor*x,scale_factor*y,-1+sc_int)
					glVertex3f(scale_factor*x,scale_factor*y,-1)
					glVertex3f(scale_factor*(x+pw),scale_factor*y,-1)
					glVertex3f(scale_factor*(x+pw),scale_factor*y,-1+sc_int)
					glEnd()

					# front
					glBegin(GL_QUADS);
					glColor3f(red/255.,green/255.,blue/255.)
					glVertex3f(scale_factor*x,scale_factor*(y-ph),-1+sc_int)
					glVertex3f(scale_factor*x,scale_factor*(y-ph),-1)
					glVertex3f(scale_factor*(x+pw),scale_factor*(y-ph),-1)
					glVertex3f(scale_factor*(x+pw),scale_factor*(y-ph),-1+sc_int)
					glEnd()

				else:
					# bottom
					glBegin(GL_QUADS);
					glColor3f(red/255.,green/255.,blue/255.)
					glVertex3f(scale_factor*x,scale_factor*y,-1)
					glVertex3f(scale_factor*x,scale_factor*(y-ph),-1)
					glVertex3f(scale_factor*(x+pw),scale_factor*(y-ph),-1)
					glVertex3f(scale_factor*(x+pw),scale_factor*y,-1)
					glEnd()

		# update the grid with the new time value
		self.grid.update(self.time)
		glutSwapBuffers()

	def keyHandler(self, key, x, y):
		dkey = key.decode("utf-8")
		if dkey == chr(27):
			sys.exit(0)
		elif dkey == chr(32):
			if self.render_3d == False:
				self.render_3d = True
			else:
				self.render_3d = False



	def main(self):
		"""
		main render function of the simulation
		initialize the grid, colormap and window
		"""
		global window
		glutInit(sys.argv)
		self.grid.init()
		self.colormap.init()

		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
		glutInitWindowSize(1000, 600)
		glutInitWindowPosition(0, 0)
		window = glutCreateWindow("PyOpenGL FDTD Simulation")
		glutDisplayFunc(self.render)
		glutIdleFunc(self.render)
		glutReshapeFunc(self.resize)
		glutKeyboardFunc(self.keyHandler)
		self.init(800, 600)
		glutMainLoop()

if __name__ == "__main__":
	sim = Simulation()
	sim.main()
