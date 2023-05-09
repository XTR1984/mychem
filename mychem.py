# -*- coding: utf-8 -*-
#from cgitb import handler
from time import sleep
#from tk import *
import tkinter as tk
import tkinter.filedialog
from math import *
import random
import os
import json
from json import encoder
import numpy as np
#encoder.FLOAT_REPR = lambda o: format(o, '.3f')

PI = 3.1415926535
from PIL import ImageGrab,ImageDraw,Image,ImageTk


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


class Node:
	def __init__(self,parent):
		self.f = 0
		self.bonded = False
		self.bonded2 = False
		self.pair = None
		self.canvas_id = None
		self.parent = parent

	def shift_q(self, n):
		#PHCSNO
		type1 = self.parent.type
		type2 = n.parent.type
		table=[5,1,4,6,3,2]
		i1 = table.index(type1)
		i2 = table.index(type2)
		canbond = False
		(ep1,ep2)=(None,None)
		for ep_i in self.parent.el_pairs:
			if canbond:
				break
			for ep_j in n.parent.el_pairs:
				if not ep_i.assigned and not ep_j.assigned and (ep_i.ecount+ep_j.ecount == 2):
					(ep1,ep2)=(ep_i,ep_j)
					ep1.assigned = True
					self.assigned_ep = ep1
					ep2.assigned = True
					n.assigned_ep = ep2
					canbond = True
					break
				
		if canbond:
			if i1<i2:
				(ep1.ecount, ep2.ecount) = (0,2)
			if i1>i2:
				(ep1.ecount, ep2.ecount) = (2,0)
			if i1==i2:
				(ep1.ecount, ep2.ecount) = (1,1)
		return canbond

	def bond(self,n):
		canbond = self.shift_q(n)
		if canbond:
			n.pair = self
			n.bonded = True
			self.pair = n
			self.bonded = True
		return canbond
	
	def unbond(self):
		if self.bonded:
			#
			#if self.assigned_ep.ecount == 1 and self.pair.assigned_ep.ecount == 1:
			#	if random.choice([False,True]):
			#		self.assigned_ep.ecount = 0
			#		self.pair.assigned_ep.ecount = 2
			#	else:
			#		self.assigned_ep.ecount = 2
			#		self.pair.assigned_ep.ecount = 0
			self.pair.assigned_ep.assigned = False
			self.pair.assigned_ep = None
			self.assigned_ep.assigned = False
			self.assigned_ep = None

			self.pair.pair = None
			self.pair.bonded = False
			self.pair.parent.bonded-=1
			self.pair = None
			self.bonded = False


class ElectronPairing():
	def __init__(self):
		self.ecount = 1
		self.assigned = False
		#self.node = None


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
		self.el_pairs = []
		self.bonded = 0
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
		if self.type==6:
			self.color = "#83ce89"
		if self.type==10:
			self.color = "green"
		if self.type==100:
			self.color = "magenta"

		if self.type<6:
			for i in range(0,self.type):
				n = Node(self)
				n.f = 2*PI/self.type*i
				self.nodes.append(n)
				ep = ElectronPairing()
				self.el_pairs.append(ep)
		elif self.type==6:
			(n1,n2) = (Node(self),Node(self))				
			n1.f = 0
			n2.f = PI
			self.nodes.extend([n1,n2])
			(ep1,ep2) = (ElectronPairing(), ElectronPairing())
			self.el_pairs.extend([ep1,ep2])
		elif self.type==10:
			(n1,n2,n3) = (Node(self),Node(self),Node(self))
			n1.f = 0
			n2.f = PI/2
			n3.f = PI
			self.nodes.extend([n1,n2,n3])

	def calculate_q(self):
		q = 0
		for ep  in self.el_pairs:
			if ep.ecount==0:
				q+=1
			if ep.ecount==2:
				q-=1
		self.q = q				
		return q
			
	def unbond(self):
		for n in self.nodes:
			if n.bonded:
				p = n.pair.parent
				n.unbond()
				p.calculate_q()	
		self.calculate_q()

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
#			self.vx = self.vx + self.ax
#			self.vy = self.vy + self.ay
#			self.vf = self.vf + self.af
#			self.x  = self.x+self.vx
#			self.y  = self.y+self.vy
#			self.f  = self.f+self.vf

			self.limits()

		

class Space:
	def __init__(self,width=1024,height=576,screenw=1024,screenh=576):
		self.ucounter = 0
		self.WIDTH=width
		self.HEIGHT=height
		self.SCREENW=screenw
		self.SCREENH=screenh
		self.ATOMRADIUS = 10
		self.BOND_KOEFF = 0.2
		self.BONDR = 4
		self.ATTRACT_KOEFF= 0.3
		#self.ATTRACTR = 5*self.ATOMRADIUS
		self.ROTA_KOEFF = 0.00005
		self.DETRACT1 = -3
		self.DETRACT_KOEFF1 = 20
		self.DETRACT2 = 3
		self.DETRACT_KOEFF2= 3
		self.MAXVELOCITY = 1
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
		self.select_mode = False
		self.select_x1 = 0
		self.select_x2 = 0
		self.select_y1 = 0
		self.select_y2 = 0
		self.select_bottomright = (0,0)
		######## tkinter ########
		self.root= tk.Tk()
		self.gravity = tk.BooleanVar()
		self.shake = tk.BooleanVar()
		self.shake.set(False)
		self.SHAKE_KOEFF = 3
		self.competitive = tk.BooleanVar()
		self.competitive.set(True)
		self.redox = tk.BooleanVar()
		self.redox.set(False)
		self.redox_rate = 1
		self.segmented_redox = tk.BooleanVar()
		self.segmented_redox.set(False)
		self.bondlock = tk.BooleanVar()
		self.bondlock.set(False)
		self.linear_field = tk.BooleanVar()
		self.linear_field.set(False)
		self.update_delta= tk.IntVar(value=5)
		self.show_q = tk.BooleanVar()
		self.show_q.set(True)
		self.root.title("Mychem")
		self.root.resizable(0, 0)
		self.menu_bar = tk.Menu(self.root)
		file_menu = tk.Menu(self.menu_bar, tearoff=False)
		file_menu.add_command(label="New", accelerator="Alt+n",command=self.file_new)
		file_menu.add_command(label="Open", accelerator="o", command=self.file_open)
		file_menu.add_command(label="Merge", accelerator="m", command=self.file_merge)
		file_menu.add_command(label="Merge recent", accelerator="l", command=self.file_merge_recent)
		file_menu.add_command(label="Save", accelerator="Alt+s", command=self.file_save)
		file_menu.add_command(label="Exit", command=self.file_exit)
		sim_menu = tk.Menu(self.menu_bar, tearoff=False)
		sim_menu.add_command(label="Go/Pause", accelerator="Space",command=self.handle_space)
		sim_menu.add_command(label="Reset", accelerator="Alt+r",command=self.reset)
		sim_menu.add_checkbutton(label="Gravity", accelerator="g", variable=self.gravity,command=self.handle_g)
		sim_menu.add_checkbutton(label="Competitive", accelerator="c", variable=self.competitive,command=self.handle_c)
		sim_menu.add_checkbutton(label="Bond lock", accelerator="b", variable=self.bondlock,command=self.handle_bondlock)
		sim_menu.add_checkbutton(label="Random shake", accelerator="s", variable=self.shake,command=self.handle_shake)
		sim_menu.add_checkbutton(label="Random redox", accelerator="r", variable=self.redox,command=self.handle_redox)
		sim_menu.add_checkbutton(label="Segmented redox",variable=self.segmented_redox)
		sim_menu.add_checkbutton(label="Linear field", accelerator="Alt-l", variable=self.linear_field,command=self.handle_fieldtype)
		
		add_menu = tk.Menu(self.menu_bar, tearoff=False)
		add_menu.add_command(label="H", accelerator="1",command=lambda:self.handle_keypress(keysym="1"))
		add_menu.add_command(label="O", accelerator="2",command=lambda:self.handle_keypress(keysym="2"))
		add_menu.add_command(label="N", accelerator="3",command=lambda:self.handle_keypress(keysym="3"))
		add_menu.add_command(label="C", accelerator="4",command=lambda:self.handle_keypress(keysym="4"))
		add_menu.add_command(label="P", accelerator="5",command=lambda:self.handle_keypress(keysym="5"))
		add_menu.add_command(label="S", accelerator="6",command=lambda:self.handle_keypress(keysym="6"))
		add_menu.add_command(label="Mixer", accelerator="0",command=lambda:self.handle_keypress(keysym="0"))
		add_menu.add_command(label="Delete", accelerator="Delete",command=self.handle_del)
		add_menu.add_command(label="Cancel", accelerator="Esc",command=self.handle_esc)
		#options_menu = tk.Menu(self.menu_bar, tearoff=False)
		examples_menu = tk.Menu(self.menu_bar, tearoff=False)
		self.create_json_menu(examples_menu,"examples/")
		view_menu = tk.Menu(self.menu_bar, tearoff=False)
		view_menu.add_command(label="View field", accelerator="f",command=self.draw_field)
		self.menu_bar.add_cascade(label="File", menu=file_menu)
		self.menu_bar.add_cascade(label="Simulation", menu=sim_menu)
		self.menu_bar.add_cascade(label="Add", menu=add_menu)
		self.menu_bar.add_cascade(label="View", menu=view_menu)
		self.menu_bar.add_command(label="Options", command=self.options_window)
		
		self.menu_bar.add_cascade(label="Examples", menu=examples_menu)
		#self.menu_bar.add_command(label="About", command=self.about_window)

		self.root.config(menu=self.menu_bar)
		self.root.bind("<space>", self.handle_space)
		self.root.bind("<Escape>", self.handle_esc)
		self.root.bind("<Delete>", self.handle_del)
		self.root.bind("<g>", self.handle_g)
		self.root.bind("<c>", self.handle_c)
		self.root.bind("<Alt-n>", self.file_new)
		self.root.bind("<m>", self.file_merge)
		self.root.bind("<l>", self.file_merge_recent)
		self.root.bind("<Alt-l>", self.handle_fieldtype)
		self.root.bind("<o>", self.file_open)
		self.root.bind("<Alt-s>", self.file_save)
		self.root.bind("<Alt-r>", self.reset)
		self.root.bind("<r>", self.handle_redox)
		self.root.bind("<s>", self.handle_shake)
		self.root.bind("<b>", self.handle_bondlock)
		self.root.bind("<Button-1>",self.handle_button1)
		self.root.bind("<Button-3>",self.handle_esc)
		self.root.bind("<KeyPress>", self.handle_keypress2)
		self.root.bind("<Motion>", self.handle_motion)
		self.root.bind("<ButtonRelease>", self.handle_release)
		self.root.bind("<MouseWheel>",self.handle_wheel)
		self.frame = tk.Frame(self.root, bd=5, relief=tk.SUNKEN)
		self.frame.pack()
		self.canvas = tk.Canvas(self.frame, width=self.WIDTH, height=self.HEIGHT, bd=0, highlightthickness=0,background="black")
		self.canvas.configure(cursor="tcross")
		self.canvas.pack()
		self.status_bar = StatusBar(self.root)
		self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
		self.status_bar.set('Ready')
		#self.canvas.update()
		if not os.path.exists('output'):
			os.makedirs('output')

	def create_json_menu(self,menu, lpath):
		files_last = []
		for filename in os.listdir(lpath):
			filepath = os.path.join(lpath, filename)
			if os.path.isdir(filepath):
				submenu = tk.Menu(menu,tearoff=False)
				menu.add_cascade(label=filename, menu=submenu)
				self.create_json_menu(submenu, filepath)
			elif os.path.splitext(filename)[-1] == ".json":
				files_last.append((filename,filepath))
		for (f,p) in files_last:				
			menu.add_command(label=f, command=lambda p2=p: self.file_merge(path=p2))
	

	def options_window(self):
		o = OptionsFrame(self)
		
	def about_window(self):
		
		a = tk.Toplevel()
		a.geometry('200x150')
		a['bg'] = 'grey'
		a.overrideredirect(True)
		tk.Label(a, text="About this")\
        	.pack(expand=1)
		a.after(5000, lambda: a.destroy())


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
		if keysym=='6':
			self.createtype=6
			self.adding_mode = True
		if keysym=='0':
			self.createtype=100
			self.adding_mode = True
		if keysym=='q':			
			self.show_q.set(not self.show_q.get())
			self.update_canvas()
		if keysym=='f':		
			self.draw_field()
		if self.adding_mode:
			self.status_bar.set("Adding element "+ str(self.createtype))
			self.numpy2atoms()
			self.make_newatom()
			self.atoms2numpy()
			self.update_canvas()
		#print(event.keysym)

	def handle_esc(self,event=None):
		if event and not self.merge_mode and not self.adding_mode and not self.moving_mode:
			self.file_merge_recent()
			return
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
			#self.atoms.remove(self.newatom)
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
					q = 0
				elif self.createtype==2:
					r = 8
					m = 16
					q = 0
				elif self.createtype==3:
					r = 9
					m = 14
					q = 0
				elif self.createtype==4:
					m = 12
					r = 10
					q = 0
				elif self.createtype==5:
					m = 31
					r = 12
					q = 0
				elif self.createtype==6:
					m = 32
					r = 12
					q = 0


				elif self.createtype==100:
					m=100
					r=10
					q = 0

				self.newatom = Atom(cx,cy,self.createtype,f=self.createf,m=m,q=q,r=r)

	def drop_atom(self):
		#self.appendatom(self.newatom)
		self.numpy2atoms()
		self.newatom.vx=0
		self.newatom.vy=0
		self.appendatom(self.newatom)
		self.newatom=None
		self.moving_mode = False
		self.status_bar.set("Dropped")
		self.atoms2numpy()
		self.update_canvas()


	def handle_space(self,event=None):
		#self.adding_mode = False
		if self.pause:
			self.sim_run()
		else:
			self.sim_pause()

	def handle_g(self,event=None):
		if event:
			self.gravity.set(not self.gravity.get())
		self.status_bar.set("Gravity is "+ OnOff(self.gravity.get()))

	def handle_fieldtype(self,event=None):
		if event:
			self.linear_field.set(not self.linear_field.get())
		self.status_bar.set("Linear field is "+ OnOff(self.linear_field.get()))


	def handle_bondlock(self,event=None):
		if event:
			self.bondlock.set(not self.bondlock.get())
		self.status_bar.set("Bondlock is "+ OnOff(self.bondlock.get()))

	def handle_redox(self,event=None):
		if event:
			self.redox.set(not self.redox.get())
		self.status_bar.set("Random redox is "+ OnOff(self.redox.get()))


	def handle_shake(self,event=None):
		if event:
			self.shake.set(not self.shake.get())
		self.status_bar.set("Random shake is "+ OnOff(self.shake.get()))


	def handle_c(self,event=None):
		if event:
			self.competitive.set(not self.competitive.get())
		self.status_bar.set("Competitive is "+ OnOff(self.competitive.get()))

	def handle_button1(self, event):
		if self.adding_mode and not self.moving_mode:
			self.numpy2atoms()
			#a= Atom(event.x,event.y, self.createtype)
			self.appendatom(self.newatom)
			#print(self.newatom.x)
			self.createf = self.newatom.f
			if self.newatom.type==100:
				self.mixers.append(self.newatom)
				self.status_bar.set("New mixer!")
			self.make_newatom()
			self.atoms2numpy()
			self.update_canvas()
		if not(self.moving_mode or self.adding_mode or self.merge_mode):
			x, y = event.x, event.y
			self.numpy2atoms()
			hitted = False
			for a in self.atoms:
				bbox = self.canvas.bbox(a.canvas_id)
				if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
					a.unbond()
					self.atoms.remove(a)
					#self.atoms2numpy()
					self.moving_offsetx = a.x-event.x
					self.moving_offsety = a.y-event.y
					self.newatom = a
					self.moving_mode = True
					self.status_bar.set("Let's move")
					hitted = True
					break
			if not hitted:
				self.select_mode = True
				self.select_x1, self.select_y1 = event.x, event.y
				self.select_x2, self.select_y2 = event.x, event.y
			self.atoms2numpy()
			self.update_canvas()
          #  	break
		elif self.moving_mode:
			self.drop_atom()
		elif self.merge_mode:
			self.numpy2atoms()
			self.atoms.extend(self.merge_atoms)
			self.mixers.extend(self.merge_mixers)
			#copy on merge with control key pressed
			if not event.state & 0x4:
				self.merge_mode=False
				self.merge_atoms = []
				self.canvas.configure(cursor="tcross")
				self.status_bar.set("Merge finished")
			else:
				new_ma = []
				for a in self.merge_atoms:
					na = Atom(a.x,a.y,a.type,a.f,a.r,a.m,a.q)
					new_ma.append(na)
				self.merge_atoms = new_ma
			self.atoms2numpy()
			self.update_canvas()
			self.resetdata = self.make_export()
		

	def handle_motion(self,event=None):
		if self.adding_mode or self.moving_mode:
			(cx,cy) = self.getpointer()
			self.newatom.x=cx+self.moving_offsetx
			self.newatom.y=cy+self.moving_offsety
			if self.pause:
				#self.atoms2numpy()
				self.update_canvas()
			return
		if self.merge_mode:
			(cx,cy) = self.getpointer()
			for a in self.merge_atoms:
				a.x = a.x - self.merge_offsetx + cx
				a.y = a.y - self.merge_offsety + cy
			self.merge_offsetx = cx
			self.merge_offsety = cy
			self.changed=True
			#self.atoms2numpy()
			self.update_canvas()
			return
		x, y = event.x, event.y			
		if self.select_mode:
			self.select_x2 = x
			self.select_y2 = y
#		self.numpy2atoms()
		for a in self.atoms:
			bbox = self.canvas.bbox(a.canvas_id)
			if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
				info = "Type=" + str(a.type)
				info += " EP state:"
				for ep in a.el_pairs:
					info+=" " + str(ep.ecount)
				for ep in a.el_pairs:
					info+=" " + str(ep.assigned)
				self.status_bar.set(info)
		if self.select_mode:
			self.update_canvas()							
		
	def handle_release(self,event=None):
		if self.select_mode:
			if self.select_x2 < self.select_x1:
				(self.select_x1, self.select_x2) = (self.select_x2, self.select_x1)
			if self.select_y2 < self.select_y1:
				(self.select_y1, self.select_y2) = (self.select_y2, self.select_y1)
			self.select_mode = False
			self.numpy2atoms()
			newatoms = []
			for a in self.atoms:
				if self.select_x1 <= a.x <= self.select_x2 and self.select_y1 <= a.y <= self.select_y2:
					a.unbond()
					self.merge_atoms.append(a)
				else:
					newatoms.append(a)
			self.atoms = newatoms
			if len(self.merge_atoms)>0:
				self.status_bar.set("Selected: "+str(len(self.merge_atoms)))
				self.atoms2numpy()
				self.merge_mode = True
				self.merge_offsetx = event.x
				self.merge_offsety = event.y
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
		self.atoms2numpy()
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
		self.atoms2numpy()					
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

	def file_merge(self,event=None, path=None):
		self.sim_pause()
		if path:
			print(path)
			fileName=path
		else:
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


		
	def reset(self,event=None):
		if not self.resetdata:
			return
		self.file_new()
		self.load_data(self.resetdata)
		self.status_bar.set("Reset to previos loaded")
	

	def update_canvas(self,noclear=False):
		#self.ucounter +=1
		#print(self.ucounter)
		if not noclear:
			self.canvas.delete("all")
		if self.redox.get() and self.segmented_redox.get():
			self.canvas.create_line(self.WIDTH/5,0,self.WIDTH/5,self.HEIGHT, fill="red")	
			self.canvas.create_line(self.WIDTH/5*4,0,self.WIDTH/5*4,self.HEIGHT, fill="blue")	
		N = len(self.atoms)
		for i in range(0,N):
			atom_i = self.atoms[i]
			atom_i.canvas_id = self.canvas.create_oval(self.np_x[i]-atom_i.r,self.np_y[i]-atom_i.r,self.np_x[i]+atom_i.r,self.np_y[i]+atom_i.r,outline=atom_i.color,fill=atom_i.color)
			for n in atom_i.nodes:
				nx = self.np_x[i] + cos(n.f+self.np_f[i])*atom_i.r
				ny = self.np_y[i] - sin(n.f+self.np_f[i])*atom_i.r
				if n.bonded:
					n.canvas_id = self.canvas.create_oval(nx-1,ny-1,nx+1,ny+1,outline=atom_i.BONDEDCOLOR,fill=atom_i.BONDEDCOLOR)
				else:
					n.canvas_id = self.canvas.create_oval(nx-1,ny-1,nx+1,ny+1,outline=atom_i.UNBONDEDCOLOR,fill=atom_i.UNBONDEDCOLOR)
			#self.canvas.create_text(self.np_x[i],self.np_y[i], text=str(i),fill="red",font="Verdana 6")
			if self.show_q.get():
				self.canvas.create_text(self.np_x[i],self.np_y[i], text=str(int(self.np_q[i])),fill="white" if atom_i.type!=4 else "black",font="Verdana 6")
		if self.adding_mode or self.moving_mode:
			self.newatom.draw(self.canvas)
		if self.merge_mode:
			for a in self.merge_atoms:
				a.draw(self.canvas)
		if self.select_mode:
			self.canvas.create_rectangle(self.select_x1,self.select_y1,self.select_x2,self.select_y2, outline="blue",dash=(5,1))
		#self.canvas.update()



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
		self.atoms2numpy()
		self.pause = False
		self.status_bar.set("Running")

	def sim_pause(self):
		self.numpy2atoms()
		self.pause = True
		self.status_bar.settime(self.t)
		self.status_bar.setinfo("Number of atoms: "+str(len(self.atoms)))
		self.status_bar.set("Paused")

	def appendatom(self,a):
		a.space = self
		self.atoms.append(a)

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
	
	def draw_field(self):
		#far field
		#return
		self.sim_pause()
		fimage = Image.new("RGB",(self.WIDTH,self.HEIGHT),(0,0,0))
		N = len(self.atoms)
		print("Calculating")
		if N<80:
			#self.status_bar.set("Calculating...")
			x = np.arange(0,self.WIDTH)
			y = np.arange(0,self.HEIGHT)
			probe_x,probe_y = np.meshgrid(x,y)
			delta_x = np.subtract.outer(probe_x.ravel(), self.np_x)
			delta_y = np.subtract.outer(probe_y.ravel(), self.np_y)
			r2 = delta_x*delta_x + delta_y*delta_y
			r = np.sqrt(r2)
			r_reciproc = np.reciprocal(r,where=r!=0)
			a= np.zeros_like(r)
			a[r<self.np_r-self.DETRACT1] = (r_reciproc*self.DETRACT_KOEFF1)[r<self.np_r-self.DETRACT1]
			a[r<self.np_r-self.DETRACT2] = (r_reciproc*self.DETRACT_KOEFF2)[r<self.np_r-self.DETRACT2]
			if self.competitive.get():	
				Q = np.outer(1, self.np_q)
				if self.linear_field.get():
					a+= Q*self.ATTRACT_KOEFF
				else:
					a+= np.divide(Q,r,where=r!=0)*self.ATTRACT_KOEFF
			#np.fill_diagonal(a,0)
			a_x = np.divide(delta_x,r,where=r!=0) *a
			a_y = np.divide(delta_y,r,where=r!=0) *a
	#		a_x = delta_x *a
	#		a_y = delta_y *a

			Ex = a_x.sum(axis=1)
			Ey = a_y.sum(axis=1)
			E2 = Ex*Ex + Ey*Ey
			E = np.sqrt(E2)
			#E = Ex+Ey
			#Emax = E.max()
			print("max=",E.max())
			print("min=",E.min())
			c = 0.005
			E = np.clip(E,0,c)
			E = E/c*255
			draw = ImageDraw.Draw(fimage)
			for y in range(0, self.HEIGHT):
				for x in range(0,self.WIDTH):
					draw.point((x,y),fill=(0,int(E[y*self.WIDTH+x]),0))
		else:
			E = np.zeros((self.WIDTH, self.HEIGHT))
			for x in range(0,self.WIDTH):
				for y in range(0,self.HEIGHT):
					delta_x = np.subtract.outer([x], self.np_x)
					delta_y = np.subtract.outer([y], self.np_y)
					r2 = delta_x*delta_x + delta_y*delta_y
					r = np.sqrt(r2)
					r_reciproc = np.reciprocal(r,where=r!=0)
					a= np.zeros_like(r)
					a[r<self.np_r-self.DETRACT1] = (r_reciproc*self.DETRACT_KOEFF1)[r<self.np_r-self.DETRACT1]
					a[r<self.np_r-self.DETRACT2] = (r_reciproc*self.DETRACT_KOEFF2)[r<self.np_r-self.DETRACT2]
					if self.competitive.get():	
						Q = np.outer(1, self.np_q)
						if self.linear_field.get():
							a+= Q*self.ATTRACT_KOEFF
						else:
							a+= np.divide(Q,r,where=r!=0)*self.ATTRACT_KOEFF
					a_x = np.divide(delta_x,r,where=r!=0) *a
					a_y = np.divide(delta_y,r,where=r!=0) *a
					Ex = a_x.sum(axis=1)
					Ey = a_y.sum(axis=1)
					E2 = Ex*Ex + Ey*Ey
					E[x,y] = np.sqrt(E2)
			print("max=",E.max())
			print("min=",E.min())
			c = 0.005
			E = np.clip(E,0,c)
			E = E/c*255
			draw = ImageDraw.Draw(fimage)
			for y in range(0, self.HEIGHT):
				for x in range(0,self.WIDTH):
					draw.point((x,y),fill=(0,int(E[x,y]),0))
		self.fphoto = ImageTk.PhotoImage(fimage)   #in self because PhotoImage garbage collected and wtf
		self.canvas.create_image(0,0,anchor="nw",image=self.fphoto)
		self.update_canvas(noclear=True)
		self.status_bar.set("Ready")

	def atoms2numpy(self):
		N = len(self.atoms)
		self.np_r = np.empty((N))
		self.np_x = np.empty((N))
		self.np_y = np.empty((N))
		self.np_vx =np.empty((N))
		self.np_vy = np.empty((N))
		self.np_ax = np.empty((N))
		self.np_ay = np.empty((N))
		self.np_f = np.empty((N))
		self.np_vf = np.empty((N))
		self.np_type = np.empty((N))
		self.np_m = np.empty((N))
		self.np_q = np.empty((N))

		for i in range(0,N):
			atom_i = self.atoms[i]
			self.np_r[i]=atom_i.r
			self.np_m[i]=atom_i.m
			self.np_x[i]=atom_i.x
			self.np_y[i]=atom_i.y
			self.np_vx[i]=atom_i.vx
			self.np_vy[i]=atom_i.vy
			self.np_ax[i]=atom_i.ax
			self.np_ay[i]=atom_i.ay
			self.np_f[i]=atom_i.f
			self.np_vf[i]=atom_i.vf
			self.np_q[i]=atom_i.q
			self.np_type[i]=atom_i.type
		self.np_SUMRADIUS = np.add.outer(self.np_r,self.np_r)
		self.np_SUMRADIUS_D1 = self.np_SUMRADIUS + self.DETRACT1
		self.np_SUMRADIUS_D2 = self.np_SUMRADIUS + self.DETRACT2

	def numpy2atoms(self):
		N = len(self.atoms)
		for i in range(0,N):
			atom_i = self.atoms[i]
			atom_i.x=self.np_x[i]
			atom_i.y=self.np_y[i]
			atom_i.vx=self.np_vx[i]
			atom_i.vy=self.np_vy[i]
			atom_i.ax=self.np_ax[i]
			atom_i.ay=self.np_ay[i]
			atom_i.f=self.np_f[i]
			atom_i.q=self.np_q[i]

	def np_next(self):
			self.np_vx *=0.9999
			self.np_vy *=0.9999
			self.np_vf *=0.99
			self.np_vx += self.np_ax
			self.np_vy += self.np_ay
			self.np_x += self.np_vx
			self.np_y += self.np_vy
			self.np_f += self.np_vf


	def np_limits(self): 
		self.np_vx[self.np_vx< -self.MAXVELOCITY] = -self.MAXVELOCITY
		self.np_vx[self.np_vx> self.MAXVELOCITY] = self.MAXVELOCITY
		self.np_vy[self.np_vy< -self.MAXVELOCITY] = -self.MAXVELOCITY
		self.np_vy[self.np_vy> self.MAXVELOCITY] = self.MAXVELOCITY
		self.np_f[self.np_f> 2*PI] -=2*PI
		self.np_f[self.np_f< 0] += 2*PI

		b = self.np_x< self.np_r
		self.np_x[b] = self.np_r[b]
		self.np_vx[b] = - self.np_vx[b]

		b = self.np_y < self.np_r
		self.np_y[b] = self.np_r[b]
		self.np_vy[b] = - self.np_vy[b]
		
		b = self.np_x > self.WIDTH-self.np_r
		self.np_x[b] = (self.WIDTH-self.np_r)[b]
		self.np_vx[b] = - self.np_vx[b]

		b = self.np_y > self.HEIGHT-self.np_r
		self.np_y[b] = (self.HEIGHT-self.np_r)[b]
		self.np_vy[b] = - self.np_vy[b]

	def go(self):	
		self.timer = 1
		#self.stoptime = 1000
		self.resetdata = self.make_export()
		self.atoms2numpy()
		self.root.after(self.timer,self.mainloop)
		self.root.mainloop()

	def mainloop(self):
			K = 1
			N = len(self.atoms)
			if self.pause:
				self.root.after(100,self.mainloop)
				return
			if N==0:
				self.sim_pause()
			self.t +=1
			Ex=np.zeros(N)
			Ey=np.zeros(N)
			a = np.zeros((N,N))
			#ones = np.ones((N,N)
#				if self.t%30==0 or self.changed==True:
#					for j in range(0,N):
#						atom_j = self.atoms[j]
#						a=0	
#						if i==j: continue
#			
#						delta_x = atom_i.x-atom_j.x
#						delta_y = atom_i.y-atom_j.y
#						r2 = delta_x*delta_x + delta_y*delta_y
#						r = sqrt(r2)
#						if r<self.ATOMRADIUS*8 and not atom_j in atom_i.near:
#							atom_i.near.append(atom_j)
#						if r>=self.ATOMRADIUS*8: 
#							try:
#								atom_i.near.remove(atom_j)
#							except:
#								pass
#
#				for atom_j in atom_i.near:
#					a=0	
			debug = False
			delta_x = np.subtract.outer(self.np_x, self.np_x)
			delta_y = np.subtract.outer(self.np_y, self.np_y)
			r2 = delta_x*delta_x + delta_y*delta_y
			r = np.sqrt(r2)
			r_reciproc = np.reciprocal(r,where=r!=0)
			a[r<self.np_SUMRADIUS_D1] = (r_reciproc*self.DETRACT_KOEFF1)[r<self.np_SUMRADIUS_D1]
			a[r<self.np_SUMRADIUS_D2] = (r_reciproc*self.DETRACT_KOEFF2)[r<self.np_SUMRADIUS_D2]
			if self.competitive.get():
						Q = np.outer(self.np_q, self.np_q)
						if self.linear_field.get():
							a+= Q*self.ATTRACT_KOEFF*0.1
						else:
							a += np.divide(Q,r,where=r!=0)*self.ATTRACT_KOEFF
			np.fill_diagonal(a,0)
			a_x = np.divide(delta_x,r,where=r!=0) *a
			a_y = np.divide(delta_y,r,where=r!=0) *a
			Ex = a_x.sum(axis=1)
			Ey = a_y.sum(axis=1)
			for i in range(0,N):
				naf = 0
				jj = np.where(np.logical_and(r[i]>0,r[i]<40))
				#print("jj=", jj)
				allnEx = 0
				allnEy = 0
				for j in jj[0].tolist():
					if j==i: continue
					atom_i = self.atoms[i]
					atom_j = self.atoms[j]
					for n1 in atom_i.nodes:
						#if self.redox.get():
						#	if n1
						n1x = self.np_x[i] + cos(n1.f+self.np_f[i])*atom_i.r
						n1y = self.np_y[i] - sin(n1.f+self.np_f[i])*atom_i.r

						nEx = 0
						nEy = 0
						naf = 0
						for n2 in atom_j.nodes:
							n2x = self.np_x[j] + cos(n2.f+self.np_f[j])*atom_j.r
							n2y = self.np_y[j] - sin(n2.f+self.np_f[j])*atom_j.r
							delta_x = n1x-n2x
							delta_y = n1y-n2y
							r2n = delta_x*delta_x + delta_y*delta_y
							rn = sqrt(r2n) 
							if rn==0: continue
							a = 0
							if rn<self.BONDR and not n1.bonded and not n2.bonded:
								if n1.bond(n2):
									self.np_q[i] = atom_i.calculate_q()
									self.np_q[j] = atom_j.calculate_q()
									self.np_vx[i] *=0.5
									self.np_vy[i] *=0.5
									self.np_vx[j] *=0.5
									self.np_vy[j] *=0.5
							if rn>self.BONDR and n1.pair == n2:
								if not self.bondlock.get():
									n1.unbond()
									self.np_q[i] = atom_i.calculate_q()
									self.np_q[j] = atom_j.calculate_q()
							if n1.pair == n2:
								if (rn>0): 
									a = -r2n*self.BOND_KOEFF
									naf += 1/rn * self.ROTA_KOEFF * (cos(n1.f+self.np_f[i])*atom_i.r * delta_y + delta_x*sin(n1.f+self.np_f[i])*atom_i.r)
									if self.redox.get():
										in_redox_zone = False
										redox_zone = -1 
										if self.segmented_redox.get() and self.np_x[i]<self.WIDTH/5*1:
											redox_zone=1
											in_redox_zone = True
										if self.segmented_redox.get() and self.np_x[i]>self.WIDTH/5*4:
											redox_zone=2
											in_redox_zone = True
										if not self.segmented_redox.get():
											redox_zone=0
											in_redox_zone = True
										if in_redox_zone and random.randint(0,5000)==1:
												pair_a = np
												(ep1, ep2) = (n1.assigned_ep, n2.assigned_ep)
												(ecount1,ecount2) = (n1.assigned_ep.ecount,n2.assigned_ep.ecount)
												n1.unbond()
												rc=random.choice([True,False])
												if (redox_zone==1) or (redox_zone==0 and rc):
													print("reduction")
													if ecount1 == 1:
														ecount1 = 2
													else:
														if ecount1 == 0:
															ecount1 = 1
														if ecount2 ==0:
															ecount2 = 1
												if (redox_zone==2) or (redox_zone==0 and not rc):
													print("oxidation")
													if ecount1 == 1:
														ecount1 = 0	
													else:
														if ecount2 ==2:
															ecount2 = 1
														if ecount1 == 2:
															ecount1 = 1
												(ep1.ecount,ep2.ecount) = (ecount1,ecount2)
												self.np_q[i] = atom_i.calculate_q()
												self.np_q[j] = atom_j.calculate_q()
							if not n1.bonded and not n2.bonded:
								naf += 1/rn * self.ROTA_KOEFF * (cos(n1.f+self.np_f[i])*atom_i.r * delta_y + delta_x*sin(n1.f+self.np_f[i])*atom_i.r)									
							nEx += delta_x/rn * a
							nEy += delta_y/rn * a

						allnEx = allnEx + nEx
						allnEy = allnEy + nEy
						self.np_vf[i] += naf

				Ex[i] += allnEx
				Ey[i] += allnEy
			self.np_ax= Ex/self.np_m
			self.np_ay= Ey/self.np_m

			if self.gravity.get():
				self.np_ay += self.g

			if self.shake.get():
				self.np_ax += self.SHAKE_KOEFF * (np.random.rand(N)-0.5)
				self.np_ay += self.SHAKE_KOEFF * (np.random.rand(N)-0.5)

			#set mixers velocity		
			if len(self.mixers)>0:
				self.np_vx[np.logical_and(self.np_type==100,self.np_vx>=0)] = 1
				self.np_vx[np.logical_and(self.np_type==100,self.np_vx<0)] = -1
				self.np_vy[np.logical_and(self.np_type==100,self.np_vy>=0)] = 1
				self.np_vy[np.logical_and(self.np_type==100,self.np_vy<0)] = -1

			if self.action:
				self.action(self)


			if self.moving_mode:
				(cx,cy) = self.getpointer()
				self.newatom.x=cx + self.moving_offsetx
				self.newatom.y=cy + self.moving_offsety

			self.np_next()
			self.np_limits()

			#update screen
			if (self.t%self.update_delta.get()==0):
				self.update_canvas()
			
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
			self.root.after(self.timer,self.mainloop)
  
class StatusBar(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		status_frame = tk.Frame(parent, bd=1, relief=tk.SUNKEN)
		status_frame.pack(side=tk.BOTTOM, fill=tk.X)
		self.label = tk.Label(status_frame, text= "Status")
		self.label.pack(side=tk.LEFT)
		self.timelabel = tk.Label(status_frame, text="Time")
		self.timelabel.pack(side=tk.RIGHT)
		self.info = tk.Label(status_frame, text="Info")
		self.info.pack(side=tk.RIGHT)

    
	def set(self, text):
		self.label.config(text=text)

	def settime(self,t):
		self.timelabel.config(text="Time:"+str(t))

	def setinfo(self,info):
		self.info.config(text=info)
    
	def clear(self):
		self.label.config(text='')

class OptionsFrame():
	def __init__(self,space):
		self.space = space
		a = tk.Toplevel()
		a.title("Options")
		a.resizable(0, 0)
		#a.geometry('200x150')
		self.frame = tk.Frame(a, bd=5, relief=tk.SUNKEN)
		self.frame.pack()
		label = tk.Label(self.frame, text= "Update delta").pack(side=tk.LEFT)
		self.update_slider = tk.Scale(self.frame, from_=1, to=100, orient=tk.HORIZONTAL,variable=self.space.update_delta)
		self.update_slider.pack()
		checkbox = tk.Checkbutton(self.frame, text="Show Q", variable=self.space.show_q)
		checkbox.pack(side=tk.LEFT)

#	def set_update_delta(self,value):
#		self.space.update_delta=value



if __name__ == "__main__":
	random.seed(1)
	space = Space()
	space.go()




