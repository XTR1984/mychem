# -*- coding: utf-8 -*-
from time import sleep
#from tkinter import *
import tkinter
import tkinter.filedialog
from math import *
import random
import os
import json
from json import encoder
#encoder.FLOAT_REPR = lambda o: format(o, '.3f')

PI = 3.1415926535
from PIL import ImageGrab


#grabbed from https://stackoverflow.com/a/71600967
def save_widget_as_image(widget, file_name):
	ImageGrab.grab(bbox=(
        widget.winfo_rootx(),
        widget.winfo_rooty(),
        widget.winfo_rootx() + widget.winfo_width(),
        widget.winfo_rooty() + widget.winfo_height()
    ),include_layered_windows=True).save(file_name)
	#exit()


class Node:
	def __init__(self):
		self.f = 0
		self.bonded = False
		self.pair = None
		self.canvas_id = None
		pass
	def bond(self,n):
		n.pair = self
		n.bonded = True
		self.pair = n
		self.bonded = True

	def unbond(self):
		if self.bonded:
			self.pair.pair = None
			self.pair.bonded = False
			self.pair = None
			self.bonded = False

class Atom:
	id = 0
	def __init__(self,x,y,type=1,f=0,r=10,m=1,q=1,fixed=False):
		Atom.id += 1
		self.id = Atom.id
		self.YSHIFT = 0
		self.x = x
		self.y = y
		self.f = f
		self.vx = 0.0
		self.vy = 0.0
		self.ax = 0.0
		self.ay = 0.0
		self.vf = 0.0
		self.af = 0.0
		self.m = m
		self.q = q
		self.type = type
		self.r = r
		self.nodes = []
		self.fixed = fixed
		self.near = []
		self.MAXVELOCITY = 1
		self.UNBONDEDCOLOR = "white"
		self.BONDEDCOLOR = "orange"
		if self.type==1:
			self.color = "blue"
		if self.type==2:
			self.color = "red"
		if self.type==3:
			self.color = "grey"
		if self.type==4:
			self.color = "yellow"
		if self.type==5:
			self.color = "brown"
		if self.type==100:
			self.color = "magenta"

		if self.type<5:
			for i in range(0,self.type):
				n = Node()
				n.f = 2*PI/self.type*i
				self.nodes.append(n)
		elif self.type==5:
			(n1,n2,n3) = (Node(),Node(),Node())
			n1.f = 0
			n2.f = PI/2
			n3.f = PI
			self.nodes.extend([n1,n2,n3])

	def draw(self,canvas):
		self.canvas_id = canvas.create_oval(self.x-self.r,self.y-self.r,self.x+self.r,self.y+self.r,outline=self.color,fill=self.color)
		for n in self.nodes:
			nx = self.x + cos(n.f+self.f)*self.r
			ny = self.y - sin(n.f+self.f)*self.r
			if n.bonded:
				n.canvas_id = canvas.create_oval(nx-1,ny-1,nx+1,ny+1,outline=self.BONDEDCOLOR,fill=self.BONDEDCOLOR)
			else:
				n.canvas_id = canvas.create_oval(nx-1,ny-1,nx+1,ny+1,outline=self.UNBONDEDCOLOR,fill=self.UNBONDEDCOLOR)



	def limits(self):
		if self.vx < -self.MAXVELOCITY: self.vx=-self.MAXVELOCITY
		if self.vx > self.MAXVELOCITY: self.vx=self.MAXVELOCITY
		if self.vy < -self.MAXVELOCITY: self.vy=-self.MAXVELOCITY
		if self.vy > self.MAXVELOCITY: self.vy=self.MAXVELOCITY

		if self.x < self.r: 
			self.vx= -self.vx
			self.x = self.r
		if self.x>self.space.WIDTH-self.r : 
			self.vx= -self.vx
			self.x = self.space.WIDTH-self.r
		if self.y < self.r:
			self.vy= -self.vy
			self.y = self.r
		if self.y>self.space.HEIGHT-self.r : 
			self.vy= -self.vy
			self.y= self.space.HEIGHT-self.r
		if self.f > 2*PI:
			self.f-= 2*PI
		if self.f < 0:
			self.f+= 2*PI

	def next(self):
		if not self.fixed:
			self.vx = self.vx + self.ax
			self.vy = self.vy + self.ay
			self.vf = self.vf + self.af
			self.x  = self.x+self.vx
			self.y  = self.y+self.vy
			self.f  = self.f+self.vf
			self.limits()

		

class Space:
	def __init__(self,width=1024,height=576,screenw=1024,screenh=576):
		self.WIDTH=width
		self.HEIGHT=height
		self.SCREENW=screenw
		self.SCREENH=screenh
		self.ATOMRADIUS = 10
		self.BOND_KOEFF = 0.2
		self.BONDR = 4
		self.ATTRACT_KOEFF= 0.01
		self.ATTRACTR = 5*self.ATOMRADIUS
		self.ROTA_KOEFF = 0.00005
		self.DETRACT1 = -3
		self.DETRACT_KOEFF1 = 15
		self.DETRACT2 = 5
		self.DETRACT_KOEFF2= 5
		self.competitive = False
		self.t = -1
		self.atoms = []	
		self.mixers = []
		self.action = None
		self.activemixer = False
		self.recording = False
		self.export = False
		self.export_file = "mychem.json"
		self.stoptime = -1
		self.pause = False
		self.g = 0.01
		self.root= tkinter.Tk()
		self.gravity = tkinter.BooleanVar()
		self.root.title("Mychem")
		self.root.resizable(0, 0)
		self.menu_bar = tkinter.Menu(self.root)
		file_menu = tkinter.Menu(self.menu_bar, tearoff=False)
		file_menu.add_command(label="New", command=self.file_new)
		file_menu.add_command(label="Open", command=self.file_open)
		file_menu.add_command(label="Save", command=self.file_save)
		file_menu.add_command(label="Exit", command=self.file_exit)
		sim_menu = tkinter.Menu(self.menu_bar, tearoff=False)
		sim_menu.add_command(label="Go/Pause", accelerator="Space",command=self.sim_pause)
		sim_menu.add_checkbutton(label="Gravity", accelerator="g", variable=self.gravity,command=self.handle_g)
		#sim_menu.add_command(label="Pause", command=self.sim_pause)
		#sim_menu.add_command(label="Reset", command=self.sim_reset)
		self.menu_bar.add_cascade(label="File", menu=file_menu)
		self.menu_bar.add_cascade(label="Simulation", menu=sim_menu)
		self.root.config(menu=self.menu_bar)
		#self.root.bind("<KeyPress>", self.handle_keypress)
		self.root.bind("<space>", self.handle_space)
		self.root.bind("<g>", self.handle_g)
		self.frame = tkinter.Frame(self.root, bd=5, relief=tkinter.SUNKEN)
		self.frame.pack()
		self.canvas = tkinter.Canvas(self.frame, width=self.WIDTH, height=self.HEIGHT, bd=0, highlightthickness=0,background="black")
		self.canvas.pack()
		self.canvas.update()
		if not os.path.exists('output'):
			os.makedirs('output')
	
	def handle_space(self,event):
		self.sim_pause()

	def handle_g(self,event):
		if self.gravity.get():
			self.gravity.set(False)
		else:
			self.gravity.set(True)
	def handle_keypress(self,event):
		if event.keysym == "32":
			self.sim_pause()
        	

	

	def file_exit(self):
		self.root.destroy()

	def file_new(self):
		self.pause=True
		self.atoms = []	
		self.mixers = []
		self.canvas.delete("all")
		
	def file_open(self):
		self.file_new()
		fileName = tkinter.filedialog.askopenfilename(title="Select file", filetypes=(("JSON files", "*.json"), ("All Files", "*.*")))
		f =  open(fileName,"r")		
		#json = f.read()
		self.resetjson = json.loads(f.read())
		self.load_json(self.resetjson)
		
	
	def load_json(self, j):
		self.atoms = []
		self.mixers = []
		for a in j["atoms"]:
			type = a["type"]
			aa = Atom(a["x"],a["y"],type=type,r=a["r"],q=a["q"],f=a["f"],m=a["m"])
			aa.vx = a["vx"]
			aa.vy = a["vy"]
			self.appendatom(aa)
			if type == 100:
				self.mixers.append(aa)

		self.canvas.delete("all")
		N = len(self.atoms)
		for i in range(0,N):
			self.atoms[i].draw(self.canvas)


	def file_save(self):
		self.pause=True
		fileName = tkinter.filedialog.asksaveasfilename(title="Save As", filetypes=(("JSON files", "*.json"), ("All Files", "*.*")))
		if not (fileName.endswith(".json") or fileName.endswith(".JSON")):
			fileName+=".json"
		f = open(fileName, "w")
		json = self.makejson()
		f.write(json)
		f.close()


	def sim_pause(self):
		if  self.pause:
			self.pause=False
		else:
			self.pause=True

	def appendatom(self,a):
		a.space = self
		self.atoms.append(a)
		#a.draw(self)

	def appendmixer(self,n=1):
		for i in range(0,n):
			m = Atom(random.randint(1,self.WIDTH),random.randint(1,self.HEIGHT),100)
			m.space = self
			m.draw(self.canvas)
			m.vx = 1
			m.vy = 1
			m.m = 20
			self.mixers.append(m)
			self.activemixer = True
			self.atoms.append(m)
	
	def makejson(self):
		frame = {}
		frame["time"] = self.t
		frame["atoms"] = []
		frame["mixers"] = []
		N = len(self.atoms)
		for i in range(0,N):
			atom = {}
			atom["id"] = self.atoms[i].id
			atom["type"] = self.atoms[i].type
			atom["x"] = round(self.atoms[i].x,4)
			atom["y"] = round(self.atoms[i].y,4)
			atom["f"] = round(self.atoms[i].f,4)
			atom["vx"] = round(self.atoms[i].vx,4)
			atom["vy"] = round(self.atoms[i].vy,4)
			atom["q"] = self.atoms[i].q
			atom["m"] = self.atoms[i].m
			atom["r"] = self.atoms[i].r
			frame["atoms"].append(atom)
		return json.dumps(frame)

	def do_export(self):
		if (not self.export):
			self.exportf = open("output/" + self.export_file, "a")
		self.exportf.write(self.makejson+"\n")

		#			j = 
	
	def go(self):	
		self.root.after(1,self.mainloop)
		self.root.mainloop()

	def mainloop(self):
			K = 1
			if self.pause:
				self.root.after(100,self.mainloop)
				return
			N = len(self.atoms)
			if N==0:
				self.sim_pause()
			self.t +=1
			for i in range(0,N):
				Ex=0
				Ey=0
				a = 0
				if self.t%30==0:
					for j in range(0,N):
						a=0	
						if i==j: continue
			
						delta_x = self.atoms[i].x-self.atoms[j].x
						delta_y = self.atoms[i].y-self.atoms[j].y
						r2 = delta_x*delta_x+ delta_y*delta_y
						r = sqrt(r2)
						if r<self.ATOMRADIUS*8 and not j in self.atoms[i].near:
							self.atoms[i].near.append(j)
						if r>=self.ATOMRADIUS*8: 
							try:
								self.atoms[i].near.remove(j)
							except:
								pass

				for j in self.atoms[i].near:
					a=0	
					if i==j: continue

					delta_x = self.atoms[i].x-self.atoms[j].x
					delta_y = self.atoms[i].y-self.atoms[j].y
					r2 = delta_x*delta_x+ delta_y*delta_y
					r = sqrt(r2)
					SUMRADIUS = self.atoms[i].r+self.atoms[j].r
					AVGRADIUS = SUMRADIUS/2
					#if r>self.ATOMRADIUS*5:continue
					if r2 == 0:
						continue;

					# a> 0 отталкивание
					if r<SUMRADIUS+self.DETRACT1:
						a = 1/r*self.DETRACT_KOEFF1

					if r<SUMRADIUS+self.DETRACT2:
						a = 1/r*self.DETRACT_KOEFF2

					Ex = Ex + delta_x/r *a
					Ey = Ey + delta_y/r *a
					#if Ex>0.1: Ex=0.1
					#if Ex<-0.1: Ex=-0.1
					#if Ey>0.1: Ey=0.1
					#if Ey<-0.1: Ey=-0.1
					allnEx = 0
					allnEy = 0
					nvf = 0

					Q = self.atoms[i].q*self.atoms[j].q
					for n1 in self.atoms[i].nodes:
						n1x = self.atoms[i].x + cos(n1.f+self.atoms[i].f)*self.atoms[i].r
						n1y = self.atoms[i].y - sin(n1.f+self.atoms[i].f)*self.atoms[i].r

						nEx = 0
						nEy = 0
						nvf = 0
						for n2 in self.atoms[j].nodes:
							n2x = self.atoms[j].x + cos(n2.f+self.atoms[j].f)*self.atoms[j].r
							n2y = self.atoms[j].y - sin(n2.f+self.atoms[j].f)*self.atoms[j].r
							delta_x = n1x-n2x
							delta_y = n1y-n2y
							#delta_f = (n1.f-self.atoms[i].f) - (n2.f-self.atoms[j].f) 
							r2 = delta_x*delta_x + delta_y*delta_y
							rn = sqrt(r2) 
							if rn==0: continue
							a = 0
							if rn<self.BONDR and not n1.bonded and not n2.bonded:
								n1.bond(n2)
								#print('bond '+str(i)+' '+str(j))
							if rn>self.BONDR and n1.pair == n2:
								n1.unbond()
								#print('unbond '+str(i)+' '+str(j))
							if n1.pair == n2:
								if (rn>0): 
									a = -r2*self.BOND_KOEFF
									nvf += 1/rn * self.ROTA_KOEFF * (cos(n1.f+self.atoms[i].f)*self.atoms[i].r * delta_y + delta_x*sin(n1.f+self.atoms[i].f)*self.atoms[i].r)
							#if not n1.bonded and not n2.bonded and rn<self.ATTRACTself.atoms[i].qR and r>self.ATOMRADIUS	:
							elif self.competitive:
								#a = -0.0005
								a = 1/rn*self.ATTRACT_KOEFF*Q
								nvf += 1/rn * self.ROTA_KOEFF * (cos(n1.f+self.atoms[i].f)*self.atoms[i].r * delta_y + delta_x*sin(n1.f+self.atoms[i].f)*self.atoms[i].r)


							nEx = nEx + delta_x/rn * a
							nEy = nEy + delta_y/rn * a

						allnEx = allnEx + nEx
						allnEy = allnEy + nEy
						self.atoms[i].vf = self.atoms[i].vf + nvf

					Ex+= allnEx
					Ey+= allnEy




				self.atoms[i].ax= K*Ex/self.atoms[i].m 
				self.atoms[i].ay= K*Ey/self.atoms[i].m				
				if self.gravity.get():
					self.atoms[i].ay +=self.g
				


		

			if self.activemixer:
				for m in self.mixers:
					if m.vx>=0:
						m.vx =1
					if m.vx<0:	
						m.vx = -1
					if m.vy>=0:
						m.vy =1
					if m.vy<0:
						m.vy = -1

			if self.action:
				self.action(self)
	
			self.canvas.delete("all")
			for i in range(0,N):
				self.atoms[i].vx *= 0.9999
				self.atoms[i].vy *= 0.9999
				self.atoms[i].vf *= 0.99
				self.atoms[i].next()
				self.atoms[i].draw(self.canvas)
			
			#  canvas.after(1)
			#	if(time%1 ==0):  
			#		for i in range(0,N):	

			self.canvas.update()
			if self.recording:
					save_widget_as_image(self.canvas,'output/'+str(self.t)+'.png')
			if self.export:
					self.do_export()

			if self.stoptime!= -1:
				if self.t>self.stoptime:
					self.sim_pause()
			


			if self.t%100 ==0:
				print(self.t)
			self.root.after(1,self.mainloop)
  

if __name__ == "__main__":
	random.seed(1)
	space = Space()
	space.go()



