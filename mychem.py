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
		self.ATTRACT_KOEFF= 0.01
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
		self.activemixer = False
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
		self.adding_mode = False
		self.moving_mode = False
		self.competitive.set(True)
		self.root.title("Mychem")
		self.root.resizable(0, 0)
		self.menu_bar = tkinter.Menu(self.root)
		file_menu = tkinter.Menu(self.menu_bar, tearoff=False)
		file_menu.add_command(label="New", accelerator="n", command=self.file_new)
		file_menu.add_command(label="Open", accelerator="o", command=self.file_open)
		file_menu.add_command(label="Save", accelerator="s", command=self.file_save)
		file_menu.add_command(label="Exit", command=self.file_exit)
		sim_menu = tkinter.Menu(self.menu_bar, tearoff=False)
		sim_menu.add_command(label="Go/Pause", accelerator="Space",command=self.handle_space)
		sim_menu.add_command(label="Reset", accelerator="r",command=self.reset)
		sim_menu.add_checkbutton(label="Gravity", accelerator="g", variable=self.gravity,command=self.handle_g)
		sim_menu.add_checkbutton(label="Competitive", accelerator="c", variable=self.competitive,command=self.handle_c)
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
		self.root.bind("<o>", self.file_open)
		self.root.bind("<s>", self.file_save)
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
		self.canvas.update()
		if not os.path.exists('output'):
			os.makedirs('output')
	
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
	def handle_del(self,event=None):
		if self.moving_mode:
			self.newatom=None
			self.moving_mode = False
			self.status_bar.set("Deleted")
			self.update_canvas()


	def make_newatom(self):
			self.newatom = None
			x = self.root.winfo_pointerx() - self.root.winfo_rootx()
			y = self.root.winfo_pointery() - self.root.winfo_rooty()
			cx = self.canvas.canvasx(x)
			cy = self.canvas.canvasy(y)
			if not self.standard:
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
					m=40
					r=10
					q = 1

				self.newatom = Atom(cx,cy,self.createtype,f=self.createf,m=m,q=q,r=r)

	def drop_atom(self):
		self.appendatom(self.newatom)
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
		self.status_bar.set("Gravity is "+ str(self.gravity.get()))

	def handle_c(self,event):
		self.competitive.set(not self.competitive.get())
		self.status_bar.set("Competitive is "+ str(self.competitive.get()))

	def handle_button1(self, event):
		if self.adding_mode and not self.moving_mode:
			#a= Atom(event.x,event.y, self.createtype)
			self.appendatom(self.newatom)
			self.createf = self.newatom.f
			if self.newatom.type==100:
				self.activemixer = True
				self.mixers.append(self.newatom)
			self.make_newatom()
			self.update_canvas()
		if not(self.moving_mode or self.adding_mode):
			x, y = event.x, event.y
			for a in self.atoms:
				bbox = self.canvas.bbox(a.canvas_id)
				if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
					a.unbond()
					#remove from nears
					#for i in range(0,len(self.atoms)):
#						for j in range(0,len(self.atom[i].near)):
					self.atoms.remove(a)
					self.newatom = a
					self.moving_mode = True
					self.status_bar.set("Let's move")
					break
			self.update_canvas()
          #  	break
		elif self.moving_mode:
			self.drop_atom()
		
	
	def handle_motion(self,event=None):
		if self.adding_mode or self.moving_mode:
			x = self.root.winfo_pointerx() - self.root.winfo_rootx()
			y = self.root.winfo_pointery() - self.root.winfo_rooty()
			cx = self.canvas.canvasx(x)
			cy = self.canvas.canvasy(y)
			self.newatom.x=cx
			self.newatom.y=cy
			self.update_canvas()
	
	def handle_wheel(self,event=None):
		if self.adding_mode or self.moving_mode:
			if event.delta>0:
				self.newatom.f += PI/18
			else:
				self.newatom.f -= PI/18
			self.status_bar.set(str(event.delta))
			self.update_canvas()





	

	def file_exit(self):
		self.root.destroy()

	def file_new(self,event=None):
		self.t = -1
		self.pause=True
		self.atoms = []	
		self.mixers = []
		self.canvas.delete("all")
		self.status_bar.set("New file")
		
	def file_open(self,event=None):
		fileName = tkinter.filedialog.askopenfilename(title="Select file", filetypes=(("JSON files", "*.json"), ("All Files", "*.*")))
		if not fileName:	
			return
		self.file_new()
		f =  open(fileName,"r")		
		#json = f.read()
		self.resetdata = json.loads(f.read())
		self.load_data(self.resetdata)
		self.status_bar.set("File loaded")
		
	def reset(self):
		self.file_new()
		self.load_data(self.resetdata)
		self.status_bar.set("Reset to previos loaded")
	
	def load_data(self, j):
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
		self.update_canvas()



	def update_canvas(self):
		self.canvas.delete("all")
		N = len(self.atoms)
		for i in range(0,N):
			self.atoms[i].draw(self.canvas)

		if self.adding_mode or self.moving_mode:
			self.newatom.draw(self.canvas)



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
			self.activemixer = True
			self.atoms.append(m)
	
	def make_export(self):
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
		return frame

	def do_export(self):
		if (not self.export):
			self.exportf = open("output/" + self.export_file, "a")
		self.exportf.write(self.make_data()+"\n")

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
				if self.t%30==0:
					for j in range(0,N):
						atom_j = self.atoms[j]
						a=0	
						if i==j: continue
			
						delta_x = atom_i.x-atom_j.x
						delta_y = atom_i.y-atom_j.y
						r2 = delta_x*delta_x+ delta_y*delta_y
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
					allnEx = 0
					allnEy = 0
					nvf = 0

					Q = atom_i.q*atom_j.q
					for n1 in atom_i.nodes:
						n1x = atom_i.x + cos(n1.f+atom_i.f)*atom_i.r
						n1y = atom_i.y - sin(n1.f+atom_i.f)*atom_i.r

						nEx = 0
						nEy = 0
						nvf = 0
						for n2 in atom_j.nodes:
							n2x = atom_j.x + cos(n2.f+atom_j.f)*atom_j.r
							n2y = atom_j.y - sin(n2.f+atom_j.f)*atom_j.r
							delta_x = n1x-n2x
							delta_y = n1y-n2y
							#delta_f = (n1.f-atom_i.f) - (n2.f-atom_j.f) 
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
									nvf += 1/rn * self.ROTA_KOEFF * (cos(n1.f+atom_i.f)*atom_i.r * delta_y + delta_x*sin(n1.f+atom_i.f)*atom_i.r)
							#if not n1.bonded and not n2.bonded and rn<self.ATTRACTatom_i.qR and r>self.ATOMRADIUS	:
							elif self.competitive.get():
								#a = -0.0005
								a = 1/rn*self.ATTRACT_KOEFF*Q
								nvf += 1/rn * self.ROTA_KOEFF * (cos(n1.f+atom_i.f)*atom_i.r * delta_y + delta_x*sin(n1.f+atom_i.f)*atom_i.r)


							nEx = nEx + delta_x/rn * a
							nEy = nEy + delta_y/rn * a

						allnEx = allnEx + nEx
						allnEy = allnEy + nEy
						atom_i.vf = atom_i.vf + nvf

					Ex+= allnEx
					Ey+= allnEy




				atom_i.ax= K*Ex/atom_i.m 
				atom_i.ay= K*Ey/atom_i.m				
				if self.gravity.get():
					atom_i.ay +=self.g
				


		

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
				atom_i=self.atoms[i]
				atom_i.vx *= 0.9999
				atom_i.vy *= 0.9999
				atom_i.vf *= 0.99
				atom_i.next()
			
			self.update_canvas()
			
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
  

class StatusBar(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.label = tkinter.Label(self, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W)
        self.label.pack(fill=tkinter.X)
    
    def set(self, text):
        self.label.config(text=text)
    
    def clear(self):
        self.label.config(text='')

if __name__ == "__main__":
	random.seed(1)
	space = Space()
	space.go()



