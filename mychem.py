# -*- coding: utf-8 -*-
from cgitb import handler
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

def OnOff(b):
	if b: return "On"
	else: return "Off"

def getpointer(self):
				x = self.root.winfo_pointerx() - self.canvas.winfo_rootx()
				y = self.root.winfo_pointery() - self.canvas.winfo_rooty()
				cx = self.canvas.canvasx(x)
				cy = self.canvas.canvasy(y)
				return (cx,cy)


class Node:
	def __init__(self,parent):
		self.f = 0
		self.bonded = False
		self.pair = None
		self.canvas_id = None
		self.parent = parent
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
				n = Node(self)
				n.f = 2*PI/self.type*i
				self.nodes.append(n)
		elif self.type==5:
			(n1,n2,n3) = (Node(self),Node(self),Node(self))
			n1.f = 0
			n2.f = PI/2
			n3.f = PI
			self.nodes.extend([n1,n2,n3])

	def calculate_q(self):
		bc = 0
		q = 0
		for n in self.nodes:
			if n.bonded:
				if self.type > n.pair.parent.type:
					q +=1
				if self.type < n.pair.parent.type:
					q -=1
		return q
			
	def unbond(self):
		for n in self.nodes:
			n.unbond()
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
		self.ATTRACT_KOEFF= 0.25
		self.ATTRACTR = 5*self.ATOMRADIUS
		self.ROTA_KOEFF = 0.00005
		self.DETRACT1 = -3
		self.DETRACT_KOEFF1 = 15
		self.DETRACT2 = 5
		self.DETRACT_KOEFF2= 5
		self.t = -1
		self.atoms = []	
		self.mixers = []
		self.action = None
		self.recording = False
		self.export = False
		self.export_file = "mychem.json"
		self.stoptime = -1
		self.pause = False
		self.g = 0.01
		self.newatom = None
		self.createtype=4
		self.createf = 0
		self.standard = True
		self.root= tkinter.Tk()
		self.gravity = tkinter.BooleanVar()
		self.competitive = tkinter.BooleanVar()
		self.competitive.set(True)
		self.bondlock = tkinter.BooleanVar()
		self.bondlock.set(False)
		self.adding_mode = False
		self.moving_mode = False
		self.changed = False
		self.moving_offsetx = 0
		self.moving_offsety = 0
		self.merge_mode = False
		self.recentdata = None
		self.resetdata = None
		self.merge_atoms = []
		self.merge_mixers = []
		self.root.title("Mychem")
		self.root.resizable(0, 0)
		self.menu_bar = tkinter.Menu(self.root)
		file_menu = tkinter.Menu(self.menu_bar, tearoff=False)
		file_menu.add_command(label="New", accelerator="n", command=self.file_new)
		file_menu.add_command(label="Open", accelerator="o", command=self.file_open)
		file_menu.add_command(label="Merge", accelerator="m", command=self.file_merge)
		file_menu.add_command(label="Merge recent", accelerator="l", command=self.file_merge_recent)
		file_menu.add_command(label="Save", accelerator="s", command=self.file_save)
		file_menu.add_command(label="Exit", command=self.file_exit)
		sim_menu = tkinter.Menu(self.menu_bar, tearoff=False)
		sim_menu.add_command(label="Go/Pause", accelerator="Space",command=self.handle_space)
		sim_menu.add_command(label="Reset", accelerator="r",command=self.reset)
		sim_menu.add_checkbutton(label="Gravity", accelerator="g", variable=self.gravity,command=self.handle_g)
		sim_menu.add_checkbutton(label="Competitive", accelerator="c", variable=self.competitive,command=self.handle_c)
		sim_menu.add_checkbutton(label="Bond lock", accelerator="b", variable=self.bondlock,command=self.handle_bondlock)
		add_menu = tkinter.Menu(self.menu_bar, tearoff=False)
		add_menu.add_command(label="H", accelerator="1",command=lambda:self.handle_keypress(keysym="1"))
		add_menu.add_command(label="O", accelerator="2",command=lambda:self.handle_keypress(keysym="2"))
		add_menu.add_command(label="N", accelerator="3",command=lambda:self.handle_keypress(keysym="3"))
		add_menu.add_command(label="C", accelerator="4",command=lambda:self.handle_keypress(keysym="4"))
		add_menu.add_command(label="X", accelerator="5",command=lambda:self.handle_keypress(keysym="5"))
		add_menu.add_command(label="Mixer", accelerator="0",command=lambda:self.handle_keypress(keysym="0"))
		add_menu.add_command(label="Delete", accelerator="Delete",command=self.handle_del)
		add_menu.add_command(label="Cancel", accelerator="Esc",command=self.handle_esc)
		

		self.menu_bar.add_cascade(label="File", menu=file_menu)
		self.menu_bar.add_cascade(label="Simulation", menu=sim_menu)
		self.menu_bar.add_cascade(label="Add", menu=add_menu)

		self.root.config(menu=self.menu_bar)
		
		self.root.bind("<space>", self.handle_space)
		self.root.bind("<Escape>", self.handle_esc)
		self.root.bind("<Delete>", self.handle_del)
		self.root.bind("<g>", self.handle_g)
		self.root.bind("<c>", self.handle_c)
		self.root.bind("<n>", self.file_new)
		self.root.bind("<m>", self.file_merge)
		self.root.bind("<l>", self.file_merge_recent)
		self.root.bind("<o>", self.file_open)
		self.root.bind("<s>", self.file_save)
		self.root.bind("<b>", self.handle_bondlock)
		self.root.bind("<Button-1>",self.handle_button1)
		self.root.bind("<Button-3>",self.handle_esc)
		self.root.bind("<KeyPress>", self.handle_keypress2)
		self.root.bind("<Motion>", self.handle_motion)
		self.root.bind("<MouseWheel>",self.handle_wheel)
		self.frame = tkinter.Frame(self.root, bd=5, relief=tkinter.SUNKEN)
		self.frame.pack()
		self.canvas = tkinter.Canvas(self.frame, width=self.WIDTH, height=self.HEIGHT, bd=0, highlightthickness=0,background="black")
		self.canvas.configure(cursor="tcross")
		self.canvas.pack()
		self.status_bar = StatusBar(self.root)
		self.status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
		self.status_bar.set('Ready')
		#self.canvas.update()
		if not os.path.exists('output'):
			os.makedirs('output')

	def getpointer(self):
				x = self.root.winfo_pointerx() - self.canvas.winfo_rootx()
				y = self.root.winfo_pointery() - self.canvas.winfo_rooty()
				cx = self.canvas.canvasx(x)
				cy = self.canvas.canvasy(y)
				return (cx,cy)


	def handle_keypress2(self,event=None):
		self.handle_keypress(keysym=event.keysym)
	
	def handle_keypress(self,keysym=""):
		if self.moving_mode:
			self.drop_atom()
		if keysym=='1':
			self.createtype=1
			self.adding_mode = True
		if keysym=='2':
			self.createtype=2
			self.adding_mode = True
		if keysym=='3':
			self.createtype=3
			self.adding_mode = True
		if keysym=='4':
			self.createtype=4
			self.adding_mode = True
		if keysym=='5':
			self.createtype=5
			self.adding_mode = True
		if keysym=='5':
			self.createtype=5
			self.adding_mode = True
		if keysym=='5':
			self.createtype=5
			self.adding_mode = True
		if keysym=='0':
			self.createtype=100
			self.adding_mode = True
		if keysym=='r':			
			self.reset()
		if self.adding_mode:
			self.status_bar.set("Adding element "+ str(self.createtype))
			self.make_newatom()
			self.update_canvas()
		#print(event.keysym)

	def handle_esc(self,event=None):
		if self.moving_mode:
			self.drop_atom()
		if self.adding_mode:
			self.newatom = None
			self.adding_mode=False
			self.update_canvas()
		if self.merge_mode:
			self.merge_atoms = []
			self.merge_mode = False
			self.canvas.configure(cursor="tcross")
			self.update_canvas()
	
	def handle_del(self,event=None):
		if self.moving_mode:
			self.atoms.remove(self.newatom)
			self.newatom=None
			self.moving_mode = False
			self.status_bar.set("Deleted")
			self.update_canvas()


	def make_newatom(self):
			self.newatom = None
			(cx,cy) = self.getpointer()
			if not self.standard:
				r = 10
				self.newatom = Atom(cx,cy,self.createtype,f=self.createf)
			else:
				if self.createtype==1:
					r = 6
					m = 1
					q = 1
				elif self.createtype==2:
					r = 8
					m = 16
					q = -1
				elif self.createtype==3:
					r = 9
					m = 14
					q = -1
				elif self.createtype==4:
					m = 12
					r = 10
					q = -1
				elif self.createtype==5:
					m = 10
					r = 10
					q = 1

				elif self.createtype==100:
					m=100
					r=10
					q = 1

				self.newatom = Atom(cx,cy,self.createtype,f=self.createf,m=m,q=q,r=r)

	def drop_atom(self):
		#self.appendatom(self.newatom)
		self.newatom.vx=0
		self.newatom.vy=0
		self.newatom=None
		self.moving_mode = False
		self.status_bar.set("Dropped")
		self.update_canvas()


	def handle_space(self,event=None):
		#self.adding_mode = False
		if self.pause:
			self.sim_run()
		else:
			self.sim_pause()

	def handle_g(self,event=None):
		self.gravity.set(not self.gravity.get())
		self.status_bar.set("Gravity is "+ OnOff(self.gravity.get()))

	def handle_bondlock(self,event=None):
		self.bondlock.set(not self.bondlock.get())
		self.status_bar.set("Bondlock is "+ OnOff(self.bondlock.get()))


	def handle_c(self,event):
		self.competitive.set(not self.competitive.get())
		self.status_bar.set("Competitive is "+ OnOff(self.competitive.get()))

	def handle_button1(self, event):
		if self.adding_mode and not self.moving_mode:
			#a= Atom(event.x,event.y, self.createtype)
			self.appendatom(self.newatom)
			self.createf = self.newatom.f
			if self.newatom.type==100:
				self.mixers.append(self.newatom)
				self.status_bar.set("New mixer!")
			self.make_newatom()
			self.update_canvas()
		if not(self.moving_mode or self.adding_mode or self.merge_mode):
			x, y = event.x, event.y
			for a in self.atoms:
				bbox = self.canvas.bbox(a.canvas_id)
				if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
					#a.unbond()
					#remove from nears
					#for i in range(0,len(self.atoms)):
#						for j in range(0,len(self.atom[i].near)):
					#self.atoms.remove(a)
					self.moving_offsetx = a.x-event.x
					self.moving_offsety = a.y-event.y
					self.newatom = a
					self.moving_mode = True
					self.status_bar.set("Let's move")
					break
			self.update_canvas()
          #  	break
		elif self.moving_mode:
			self.drop_atom()
		elif self.merge_mode:
			self.merge_mode=False
			self.atoms.extend(self.merge_atoms)
			self.mixers.extend(self.merge_mixers)
			self.merge_atoms = []
			self.merge_mixers = []
			self.canvas.configure(cursor="tcross")
			self.update_canvas()
			self.resetdata = self.make_export()
			self.status_bar.set("Merge finished")
	
	def handle_motion(self,event=None):
		if self.adding_mode or self.moving_mode:
			(cx,cy) = self.getpointer()
			self.newatom.x=cx+self.moving_offsetx
			self.newatom.y=cy+self.moving_offsety
			if self.pause:
				self.update_canvas()
		if self.merge_mode:
			(cx,cy) = self.getpointer()
			for a in self.merge_atoms:
				a.x = a.x - self.merge_offsetx + cx
				a.y = a.y - self.merge_offsety + cy
			self.merge_offsetx = cx
			self.merge_offsety = cy
			self.changed=True
			self.update_canvas()
	
	def handle_wheel(self,event=None):
		if self.adding_mode or self.moving_mode:
			if event.delta>0:
				self.newatom.f += PI/18
			else:
				self.newatom.f -= PI/18
			self.status_bar.set(str(event.delta))
			self.update_canvas()
		if self.merge_mode:
			f=0
			if event.delta>0:
				f += PI/18
			else:
				f -= PI/18
			for a in self.merge_atoms:
				(cx,cy) = self.getpointer()
				#a.x = a.x - self.merge_offsetx
				#a.y = a.y - self.merge_offsety
				a.x -=cx
				a.y -=cy
				(a.x, a.y) = ( a.x*cos(f) - a.y*sin(f) , a.x*sin(f) + a.y*cos(f))
				a.x += cx
				a.y += cy
				a.f -= f
			self.update_canvas()


	def file_new(self,event=None):
		self.t = -1
		self.pause=True
		self.atoms = []	
		self.mixers = []
		self.canvas.delete("all")
		self.status_bar.set("New file")



	def load_data(self, j, merge=False):
		if not merge: 
			self.atoms = []
			self.mixers = []
		for a in j["atoms"]:
			type = a["type"]
			aa = Atom(a["x"],a["y"],type=type)
			aa.vx = a["vx"]
			aa.vy = a["vy"]
			aa.r=a["r"]
			aa.q=a["q"]
			aa.f=a["f"]
			aa.m=a["m"]
			if merge:
				aa.space = self
				(self.merge_offsetx, self.merge_offsety) =  (self.WIDTH/2,self.HEIGHT/2)
				(cx,cy) = self.getpointer()
				aa.x = aa.x - self.merge_offsetx + cx
				aa.y = aa.y - self.merge_offsety + cy
				(self.merge_offsetx, self.merge_offsety) = (cx,cy)
				self.merge_atoms.append(aa)
				if type == 100:
					self.merge_mixers.append(aa)
			else:
				self.appendatom(aa)
				if type == 100:
					self.mixers.append(aa)
		self.update_canvas()


	def file_open(self,event=None):
		fileName = tkinter.filedialog.askopenfilename(title="Select file", filetypes=(("JSON files", "*.json"), ("All Files", "*.*")))
		if not fileName:	
			return
		self.file_new()
		f =  open(fileName,"r")		
		self.resetdata = json.loads(f.read())
		self.load_data(self.resetdata)
		self.status_bar.set("File loaded")

	def file_merge(self,event=None):
		self.sim_pause()
		fileName = tkinter.filedialog.askopenfilename(title="Select file", filetypes=(("JSON files", "*.json"), ("All Files", "*.*")))
		if not fileName:	
			return
		f =  open(fileName,"r")		
		self.merge_atoms = []
		mergedata = json.loads(f.read())
		self.recentdata = mergedata
		self.merge_mode=True
		self.load_data(mergedata, merge=True)
		self.canvas.configure(cursor="hand2")
		self.status_bar.set("Merging mode")

	def file_merge_recent(self,event=None):
		if not self.recentdata:
			return
		self.sim_pause()
		self.merge_atoms = []
		self.merge_mode=True
		self.load_data(self.recentdata, merge=True)
		self.canvas.configure(cursor="hand2")
		self.status_bar.set("Merging mode")

	def file_exit(self):
		self.root.destroy()


		
	def reset(self):
		if not self.resetdata:
			return
		self.file_new()
		self.load_data(self.resetdata)
		self.status_bar.set("Reset to previos loaded")
	



	def update_canvas(self):
		self.canvas.delete("all")
		for a in self.atoms:
			a.draw(self.canvas)

		if self.adding_mode or self.moving_mode:
			self.newatom.draw(self.canvas)
		if self.merge_mode:
			for a in self.merge_atoms:
				a.draw(self.canvas)
		self.canvas.update()



	def file_save(self,event=None):
		self.pause=True
		fileName = tkinter.filedialog.asksaveasfilename(title="Save As", filetypes=(("JSON files", "*.json"), ("All Files", "*.*")))
		if not (fileName.endswith(".json") or fileName.endswith(".JSON")):
			fileName+=".json"
		f = open(fileName, "w")
		self.resetdata = self.make_export()
		f.write(json.dumps(self.resetdata))
		f.close()
		self.status_bar.set("File saved")


	def sim_run(self):
		self.pause = False
		self.status_bar.set("Running")

	def sim_pause(self):
		self.pause = True
		self.status_bar.set("Paused")

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
			m.m = 40
			self.mixers.append(m)
			self.atoms.append(m)
	
	def make_export(self):
		frame = {}
		frame["time"] = self.t
		frame["atoms"] = []
		#frame["mixers"] = []
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
		return frame

	def do_export(self):
		if (not self.export):
			self.exportf = open("output/" + self.export_file, "a")
		self.exportf.write(self.make_export()+"\n")

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
				atom_i = self.atoms[i]
				Ex=0
				Ey=0
				a = 0
				if self.t%30==0 or self.changed==True:
					for j in range(0,N):
						atom_j = self.atoms[j]
						a=0	
						if i==j: continue
			
						delta_x = atom_i.x-atom_j.x
						delta_y = atom_i.y-atom_j.y
						r2 = delta_x*delta_x + delta_y*delta_y
						r = sqrt(r2)
						if r<self.ATOMRADIUS*8 and not atom_j in atom_i.near:
							atom_i.near.append(atom_j)
						if r>=self.ATOMRADIUS*8: 
							try:
								atom_i.near.remove(atom_j)
							except:
								pass

				for atom_j in atom_i.near:
					a=0	
					delta_x = atom_i.x-atom_j.x
					delta_y = atom_i.y-atom_j.y
					r2 = delta_x*delta_x+ delta_y*delta_y
					r = sqrt(r2)
					SUMRADIUS = atom_i.r+atom_j.r
					#AVGRADIUS = SUMRADIUS/2
					if r2 == 0:
						continue;

					# a> 0 отталкивание
					if r<SUMRADIUS+self.DETRACT1:
						a = 1/r*self.DETRACT_KOEFF1

					if r<SUMRADIUS+self.DETRACT2:
						a = 1/r*self.DETRACT_KOEFF2

					if self.competitive.get() and not atom_i.type==100:
						Q = atom_i.q*atom_j.q
						a+= Q/r*self.ATTRACT_KOEFF

					Ex = Ex + delta_x/r *a
					Ey = Ey + delta_y/r *a
					allnEx = 0
					allnEy = 0
					naf = 0


					for n1 in atom_i.nodes:
						n1x = atom_i.x + cos(n1.f+atom_i.f)*atom_i.r
						n1y = atom_i.y - sin(n1.f+atom_i.f)*atom_i.r

						nEx = 0
						nEy = 0
						naf = 0
						for n2 in atom_j.nodes:
							n2x = atom_j.x + cos(n2.f+atom_j.f)*atom_j.r
							n2y = atom_j.y - sin(n2.f+atom_j.f)*atom_j.r
							delta_x = n1x-n2x
							delta_y = n1y-n2y
							r2n = delta_x*delta_x + delta_y*delta_y
							rn = sqrt(r2n) 
							if rn==0: continue
							a = 0
							if rn<self.BONDR and not n1.bonded and not n2.bonded:
								n1.bond(n2)
#								self.calculate_q(atom_i)	
#								self.calculate_q(atom_j)
							if rn>self.BONDR and n1.pair == n2:
								if not self.bondlock.get():
									n1.unbond()
#									self.calculate_q(atom_i)	
#									self.calculate_q(atom_j)
							if n1.pair == n2:
								if (rn>0): 
									a = -r2n*self.BOND_KOEFF
									naf += 1/rn * self.ROTA_KOEFF * (cos(n1.f+atom_i.f)*atom_i.r * delta_y + delta_x*sin(n1.f+atom_i.f)*atom_i.r)
							#if not n1.bonded and not n2.bonded and rn<self.ATTRACTatom_i.qR and r>self.ATOMRADIUS	:
							#if self.competitive.get():
							#	a += 1/rn*self.ATTRACT_KOEFF*Q
							#	naf += 1/rn * self.ROTA_KOEFF * (cos(n1.f+atom_i.f)*atom_i.r * delta_y + delta_x*sin(n1.f+atom_i.f)*atom_i.r)


							nEx = nEx + delta_x/rn * a
							nEy = nEy + delta_y/rn * a

						allnEx = allnEx + nEx
						allnEy = allnEy + nEy
						atom_i.vf = atom_i.vf + naf

					Ex+= allnEx
					Ey+= allnEy
				atom_i.ax= K*Ex/atom_i.m 
				atom_i.ay= K*Ey/atom_i.m				
				if self.gravity.get():
					atom_i.ay +=self.g

			if len(self.mixers)>0:
				for m in self.mixers:
#						m.vx*=1.1
#						m.vy*=1.1
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

			if self.moving_mode:
				(cx,cy) = self.getpointer()
				self.newatom.x=cx + self.moving_offsetx
				self.newatom.y=cy + self.moving_offsety


			for i in range(0,N):
				atom_i=self.atoms[i]
				atom_i.vx *= 0.9999
				atom_i.vy *= 0.9999
				atom_i.vf *= 0.99
				atom_i.calculate_q()
				atom_i.next()
			
			self.update_canvas()
			
			#  canvas.after(1)
			#	if(time%1 ==0):  
			#		for i in range(0,N):	


			if self.recording:
					save_widget_as_image(self.canvas,'output/'+str(self.t)+'.png')
			if self.export:
					self.do_export()

			if self.stoptime!= -1:
				if self.t>self.stoptime:
					self.sim_pause()
			


			if self.t%100 ==0:
				self.status_bar.settime(self.t)
				self.status_bar.setinfo("Number of atoms: "+str(N))
			self.root.after(1,self.mainloop)
  

class StatusBar(tkinter.Frame):
	def __init__(self, master):
		super().__init__(master)
		status_frame = tkinter.Frame(master, bd=1, relief=tkinter.SUNKEN)
		status_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)
		self.label = tkinter.Label(status_frame, text= "Status")
		self.label.pack(side=tkinter.LEFT)
		self.timelabel = tkinter.Label(status_frame, text="Time")
		self.timelabel.pack(side=tkinter.RIGHT)
		self.info = tkinter.Label(status_frame, text="Info")
		self.info.pack(side=tkinter.RIGHT)


		
    
	def set(self, text):
		self.label.config(text=text)

	def settime(self,t):
		self.timelabel.config(text="Time:"+str(t))

	def setinfo(self,info):
		self.info.config(text=info)

    
	def clear(self):
		self.label.config(text='')

if __name__ == "__main__":
	random.seed(1)
	space = Space()
	space.go()



