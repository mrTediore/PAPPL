import random, warnings
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys
import numpy as np
import timeit

resolution = sys.argv[1]
repertoire = str(sys.argv[2]) + "/"

imgs = os.listdir(repertoire)


class AutoScrollbar(ttk.Scrollbar):
	''' A scrollbar that hides itself if it's not needed.
		Works only if you use the grid geometry manager '''
	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			self.grid_remove()
		else:
			self.grid()
			ttk.Scrollbar.set(self, lo, hi)

	def pack(self, **kw):
		raise tk.TclError('Cannot use pack with this widget')

	def place(self, **kw):
		raise tk.TclError('Cannot use place with this widget')

class Zoom_Advanced(ttk.Frame):
	''' Advanced zoom of the image '''
	def __init__(self, mainframe):
		''' Initialize the main Frame '''
		ttk.Frame.__init__(self, master=mainframe)
		self.master.title('Zoom with mouse wheel')
		# Vertical and horizontal scrollbars for canvas
		vbar = AutoScrollbar(self.master, orient='vertical')
		hbar = AutoScrollbar(self.master, orient='horizontal')
		vbar.grid(row=0, column=1, sticky='ns')
		hbar.grid(row=1, column=0, sticky='we')
		# Create canvas and put image on it
		self.canvas = tk.Canvas(self.master, highlightthickness=0,
								xscrollcommand=hbar.set, yscrollcommand=vbar.set)
		self.canvas.grid(row=0, column=0, sticky='nswe')
		self.canvas.update()  # wait till canvas is created
		vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
		hbar.configure(command=self.scroll_x)
		# Make the canvas expandable
		self.master.rowconfigure(0, weight=1)
		self.master.columnconfigure(0, weight=1)
		# Bind events to the Canvas
		self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
		self.canvas.bind('<ButtonPress-1>', self.move_from)
		self.canvas.bind('<B1-Motion>',     self.move_to)
		self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
		self.canvas.bind('<Shift-MouseWheel>', self.wheel)
		self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
		self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
		self.resolution = resolution

		self.configurate_canvas("C400-Mesh",str(resolution),imgs)

	def configurate_canvas(self,nom,resolution,images,xmove=0.0,ymove=0.0):
		self.canvas.delete("all")
		self.images = self.selection_images(nom,resolution,images)

		self.image00 = Image.open(repertoire + self.images[0][0])  # open image
		if self.dimX > 0:
			self.image10 = Image.open(repertoire + self.images[1][0])
		if self.dimY > 0:
			self.image01 = Image.open(repertoire + self.images[0][1])
		if self.dimX > 0 and self.dimY > 0:
			self.image11 = Image.open(repertoire + self.images[1][1])

		self.tuple00 = (0,0)
		self.tuple10 = (1,0)
		self.tuple01 = (0,1)
		self.tuple11 = (1,1)

		self.width = self.image00.size[0] * 2
		self.height = self.image00.size[1] * 2

		self.imscale = 1.0  # scale for the canvas image
		self.delta = 1.3  # zoom magnitude

		# Put image into container rectangle and use it to set proper coordinates to the image
		self.container = self.canvas.create_rectangle(0, 0, resolution, resolution, width=0)

		self.canvas.configure(scrollregion=(1,1,int(resolution)-1,int(resolution)-1))
		bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
				 self.canvas.canvasy(0),
				 self.canvas.canvasx(self.canvas.winfo_width()),
				 self.canvas.canvasy(self.canvas.winfo_height()))

		self.canvas.xview_moveto(xmove)
		self.canvas.yview_moveto(ymove)
		self.canvas.update()

		self.initial_show_image()

	def selection_images(self,nom,resolution,images):
		self.dimX = 0
		self.dimY = 0
		count= 0
		split = []
		#print(nom, " ", resolution)
		for image in images:
			split = image.split('.')[0]
			split = split.split('_')
			if split[0]==nom and split[1]==resolution:
				count += 1
				if int(split[2]) > self.dimX:
					self.dimX = int(split[2])
				if int(split[3]) > self.dimY:
					self.dimY = int(split[3])

		liste = np.zeros((self.dimX + 1,self.dimY + 1),dtype = object)

		for image in images:
			split = image.split('.')[0]
			split = split.split('_')
			if split[0]==nom and split[1]==resolution:
				liste[int(split[2])][int(split[3])] = image

		return(liste)

	def detect_resolution(self,nom,resolution,images):
		for image in images:
			split = image.split('.')[0]
			split = split.split('_')
			if split[0]==nom and split[1]==resolution:
				return True
		return False

	def scroll_y(self, *args, **kwargs):
		''' Scroll canvas vertically and redraw the image '''
		self.canvas.yview(*args, **kwargs)  # scroll vertically
		self.show_image()  # redraw the image

	def scroll_x(self, *args, **kwargs):
		''' Scroll canvas horizontally and redraw the image '''
		self.canvas.xview(*args, **kwargs)  # scroll horizontally
		self.show_image()  # redraw the image

	def move_from(self, event):
		''' Remember previous coordinates for scrolling with the mouse '''
		self.canvas.scan_mark(event.x, event.y)

	def move_to(self, event):

		''' Drag (move) canvas to the new position '''
		self.canvas.scan_dragto(event.x, event.y, gain=1)
		self.show_image()  # redraw the image

	def change_image(self,intx,inty,newx,newy):
		if intx == 0:
			if inty == 0:
				self.tuple00 = (newx,newy)
				self.image00 = Image.open(repertoire + self.images[newx][newy])
			else:
				self.tuple01 = (newx,newy)
				self.image01 = Image.open(repertoire + self.images[newx][newy])
		else:
			if inty == 0:
				self.tuple10 = (newx,newy)
				self.image10 = Image.open(repertoire + self.images[newx][newy])
			else:
				self.tuple11 = (newx,newy)
				self.image11 = Image.open(repertoire + self.images[newx][newy])

	def wheel(self, event):
		''' Zoom with mouse wheel '''

		bbox1 = self.canvas.bbox(self.container)  # get image area

		sizex = np.abs(bbox1[2] - bbox1[0])
		sizey = np.abs(bbox1[3] - bbox1[1])
		titleDimX = sizex//(self.dimX+1)
		titleDimY = sizey//(self.dimY+1)
		bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)

		bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
				 self.canvas.canvasy(0),
				 self.canvas.canvasx(self.canvas.winfo_width()),
				 self.canvas.canvasy(self.canvas.winfo_height()))
		
		bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
				max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
		
		if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
			bbox[0] = bbox1[0]
			bbox[2] = bbox1[2]
		if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
			bbox[1] = bbox1[1]
			bbox[3] = bbox1[3]
		self.canvas.configure(scrollregion=bbox)  # set scroll region
		x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
		y1 = max(bbox2[1] - bbox1[1], 0)
		x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
		y2 = min(bbox2[3], bbox1[3]) - bbox1[1]

		xratio = x1 / (bbox[2]-bbox[0])
		yratio = y1 / (bbox[3]-bbox[1])
		print("ratio ",xratio , yratio)

		if np.abs(x2 - x1)*self.delta > 2 * titleDimX or np.abs(y2 - y1)*self.delta > 2 * titleDimY:
			return
		else:
			

			x = self.canvas.canvasx(event.x)
			y = self.canvas.canvasy(event.y)
			bbox = self.canvas.bbox(self.container)  # get image area
			if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
			else: return  # zoom only inside image area
			scale = 1.0
			# Respond to Linux (event.num) or Windows (event.delta) wheel event
			if event.num == 5 or event.delta <= 0:  # scroll down
				i = min(self.width, self.height)
				#if int(i * self.imscale) < 1000: return  # image is less than 30 pixels
				self.imscale /= self.delta
				scale        /= self.delta

				if self.imscale < (self.delta / 4):
					if self.detect_resolution("C400-Mesh",str(int(self.resolution) // 2),imgs):
						self.canvas.delete('r')
						self.resolution = str(int(self.resolution) // 2)
						self.configurate_canvas("C400-Mesh",self.resolution,imgs,xratio,yratio)
						return
					else:
						if self.dimX == 0 and self.dimY == 0 :
							if self.imscale < (self.delta / 15):
								self.imscale = self.imscale * self.delta
								return
						else:
							self.imscale = self.imscale * self.delta
							return
				else:
					self.canvas.delete('r')

			if event.num == 4 or event.delta > 0:  # scroll up
				i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
				if i < self.imscale: return  # 1 pixel is bigger than the visible area
				self.imscale *= self.delta
				scale        *= self.delta

				if self.imscale > (self.delta*3):
					if self.detect_resolution("C400-Mesh",str(int(self.resolution) * 2),imgs):
						self.canvas.delete('r')
						self.resolution = str(int(self.resolution) * 2)
						self.configurate_canvas("C400-Mesh",self.resolution,imgs,xratio,yratio)
						return
					else:
						self.imscale = self.imscale / self.delta
						return
				else:
					self.canvas.delete('r')
					

			self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
			self.show_image()

	def initial_show_image(self, event=None):
		
		print("chargement")

		#self.canvas.update()
		
		self.show_image()

	def show_image(self, event=None):
		''' Show image on the Canvas '''
		bbox1 = self.canvas.bbox(self.container)  # get image area

		sizex = np.abs(bbox1[2] - bbox1[0])
		sizey = np.abs(bbox1[3] - bbox1[1])
		titleDimX = sizex//(self.dimX+1)
		titleDimY = sizey//(self.dimY+1)

		#print(np.abs(bbox1[2] - bbox1[0]))
		#print(self.dimX,self.dimY)
		#print(titleDimX,titleDimY) 

		# Remove 1 pixel shift at the sides of the bbox1
		bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)

		bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
				 self.canvas.canvasy(0),
				 self.canvas.canvasx(self.canvas.winfo_width()),
				 self.canvas.canvasy(self.canvas.winfo_height()))
		
		bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
				max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
		
		if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
			bbox[0] = bbox1[0]
			bbox[2] = bbox1[2]
		if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
			bbox[1] = bbox1[1]
			bbox[3] = bbox1[3]
		self.canvas.configure(scrollregion=bbox)  # set scroll region
		x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
		y1 = max(bbox2[1] - bbox1[1], 0)
		x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
		y2 = min(bbox2[3], bbox1[3]) - bbox1[1]

		tx1 = int(x1 // titleDimX)
		ty1 = int(y1 // titleDimY)
		qx1 = x1 % titleDimX
		qy1 = y1 % titleDimY
		if tx1 < 0:
			tx1 = 0
			qx1 = 0
		if ty1 < 0:
			ty1 = 0
			qy1 = 0

		tx2 = int(x2 // titleDimX)
		ty2 = int(y2 // titleDimY)
		qx2 = x2 % titleDimX
		qy2 = y2 % titleDimY

		if tx2 > self.dimX:
			tx2 = self.dimX
			qx2 = 0
		if ty2 > self.dimY:
			ty2 = self.dimY
			qy2 = 0

		if (tx1,ty1) != self.tuple00:
			self.change_image(0,0,int(tx1),int(ty1))
			
		xt = self.tuple00[0] * titleDimX
		yt = self.tuple00[1] * titleDimY


		if tx1 == tx2 :

			if ty1 == ty2 :
				image00 = self.image00.crop((int((x1 - xt)/ self.imscale), int((y1 - yt)/ self.imscale), 
					int((x2 -xt)/ self.imscale),int((y2 -yt)/ self.imscale)))
				imagetk00 = ImageTk.PhotoImage(image00.resize((int(x2 - x1), int(y2 - y1))))
				imageid00 = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
					anchor='nw', image=imagetk00, tags ='r')

				self.canvas.lower(imageid00)  # set image into background
				self.canvas.imagetk00 = imagetk00  # keep an extra reference to prevent garbage-collection

			else:
				if(tx1,ty2) != self.tuple01:
					self.change_image(0,1,int(tx1),int(ty2))

				image00 = self.image00.crop((int((x1 -xt)/ self.imscale), int((y1 -yt)/ self.imscale),
					int((x2 -xt)/ self.imscale),int((titleDimY)/ self.imscale)))
				imagetk00 = ImageTk.PhotoImage(image00.resize((int(x2 - x1), int(titleDimY - y1 + yt))))
				imageid00 = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
					anchor='nw', image=imagetk00, tags ='r')
				self.canvas.lower(imageid00)  # set image into background
				self.canvas.imagetk00 = imagetk00

				if qy2 > 0:

					image01 = self.image01.crop((int((x1 -xt)/ self.imscale),0,
						int((x2 -xt)/ self.imscale),int(qy2 / self.imscale)))
					imagetk01 = ImageTk.PhotoImage(image01.resize((int(x2 - x1), int(qy2))))
					imageid01 = self.canvas.create_image(max(bbox2[0], bbox1[0]),max(bbox2[1], bbox1[1])+int(titleDimY - y1 + yt),
						anchor='nw', image=imagetk01, tags = 'r')
					self.canvas.lower(imageid01)
					self.canvas.imagetk01 = imagetk01

		else:
			if ty1 == ty2:
					
				if(tx2,ty1) != self.tuple10:
					self.change_image(1,0,int(tx2),int(ty1))

				image00 = self.image00.crop((int((x1 -xt)/ self.imscale), int((y1 -yt)/ self.imscale),
					int((titleDimX)/ self.imscale),int((y2 -yt)/ self.imscale)))
				imagetk00 = ImageTk.PhotoImage(image00.resize((int(titleDimX - x1 + xt), int(y2 - y1))))
				imageid00 = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
					anchor='nw', image=imagetk00, tags ='r')
				self.canvas.lower(imageid00)  # set image into background
				self.canvas.imagetk00 = imagetk00

				if qx2 > 0:

					image10 = self.image10.crop((0,int((y1 -yt)/ self.imscale),
						int(qx2/ self.imscale),int((y2 - yt)/ self.imscale)))
					imagetk10 = ImageTk.PhotoImage(image10.resize((int(qx2), int(y2-y1))))
					imageid10 = self.canvas.create_image(max(bbox2[0], bbox1[0])+int(titleDimX - x1 + xt),max(bbox2[1], bbox1[1]),
						anchor='nw', image=imagetk10, tags = 'r')
					self.canvas.lower(imageid10)
					self.canvas.imagetk10 = imagetk10



			else:
				if(tx2,ty1) != self.tuple10:
					self.change_image(1,0,int(tx2),int(ty1))
				if(tx1,ty2) != self.tuple01:
					self.change_image(0,1,int(tx1),int(ty2))
				if(tx2,ty2) != self.tuple11:
					self.change_image(1,1,int(tx2),int(ty2))
					
				image00 = self.image00.crop((int((x1 -xt)/ self.imscale), int((y1 -yt)/ self.imscale),
					int((titleDimX)/ self.imscale),int((titleDimY)/ self.imscale)))
				imagetk00 = ImageTk.PhotoImage(image00.resize((int(titleDimX - x1 + xt), int(titleDimY - y1 + yt))))
				imageid00 = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
					anchor='nw', image=imagetk00, tags ='r')
				self.canvas.lower(imageid00)  # set image into background
				self.canvas.imagetk00 = imagetk00

				if qy2 > 0:

					image01 = self.image01.crop((int((x1 -xt)/ self.imscale),0,
						int((titleDimX)/ self.imscale),int(qy2 / self.imscale)))
					imagetk01 = ImageTk.PhotoImage(image01.resize((int(titleDimX - x1 + xt), int(qy2))))
					imageid01 = self.canvas.create_image(max(bbox2[0], bbox1[0]),max(bbox2[1], bbox1[1])+int(titleDimY - y1 + yt),
						anchor='nw', image=imagetk01, tags = 'r')
					self.canvas.lower(imageid01)
					self.canvas.imagetk01 = imagetk01

				if qx2 > 0:

					image10 = self.image10.crop((0,int((y1 -yt)/ self.imscale),
						int(qx2/ self.imscale),int((titleDimY)/ self.imscale)))
					imagetk10 = ImageTk.PhotoImage(image10.resize((int(qx2), int(titleDimY - y1 + yt))))
					imageid10 = self.canvas.create_image(max(bbox2[0], bbox1[0])+int(titleDimX - x1 + xt),max(bbox2[1], bbox1[1]),
						anchor='nw', image=imagetk10, tags = 'r')
					self.canvas.lower(imageid10)
					self.canvas.imagetk10 = imagetk10

				if qx2 > 0 and qy2 > 0:

					image11 = self.image11.crop((0,0,
						int(qx2/ self.imscale),int(qy2 / self.imscale)))
					imagetk11 = ImageTk.PhotoImage(image11.resize((int(qx2),int(qy2))))

					imageid11 = self.canvas.create_image(max(bbox2[0], bbox1[0])+int(titleDimX - x1 + xt),max(bbox2[1], bbox1[1])+int(titleDimY - y1 + yt),
						anchor='nw', image=imagetk11, tags = 'r')

					self.canvas.lower(imageid11)
					self.canvas.imagetk11 = imagetk11

root = tk.Tk()
root.geometry('700x700') # Size 200, 200
app = Zoom_Advanced(root)
root.mainloop()
