import tkinter as tk
import threading
import webbrowser
import tkMessageBox
import subprocess
import os
import sys
from PIL import Image, ImageTk

#custom libraries
import alarmRectifier
#custom libraries ends
backgroundColor='#27ae60'
mainButtonColor='#9b59b6'

LARGE_FONT= ("Open Sans", 27,'bold')
def_font=("Open Sans", 13,'bold')
sm_font=("Open Sans", 9,'bold')

def fun(button1,resultLocation,Lb):
	button1['state'] = 'disable'
	resultLocation['state'] = 'disable'

	x=lambda: threading.Thread(target=alarmRectifier.mainFunc, 
	    args= ( button1 , resultLocation , Lb) ).start()
	
	x()

if __name__ == '__main__':

	if not os.path.exists('result'):
		os.makedirs('result')

	root = tk.Tk() 

	if getattr(sys, 'frozen', False):
	    image_file_path =os.path.join(sys._MEIPASS, "photos/pic.png")
	else:
	    image_file_path = "photos/pic.png"


	load = Image.open(image_file_path) ## image background
	load=load.resize((80, 80), Image.ANTIALIAS)
	render = ImageTk.PhotoImage(load)
	img = tk.Label(root, image=render)
	img.image = render
	img.place(x=10, y=10) ## image ends

	label = tk.Label(root, text="Alarm Rectification Tool",fg='white',bg=backgroundColor,font=LARGE_FONT)
	label.pack(pady=2,padx=10)

	button1 = tk.Button(root, text=" Generate Output ", cursor="hand2", font=def_font,height = 2, width = 20,bg=mainButtonColor,fg='white')
	button1.pack(pady=5,padx=5)

	resultLocation = tk.Button(root, text='Open Result Location', cursor="hand2", font=def_font,height = 2, width = 20)
	resultLocation.pack(pady=5,padx=5)

	frame = tk.Frame(root)
	frame.pack(padx=10,pady=20)

	scrollbar = tk.Scrollbar(frame,orient="vertical") 

	Lb = tk.Listbox(frame,width=150,height=12,yscrollcommand = scrollbar.set,font=sm_font)

	Lb.insert(tk.END, 'Program is ready to use please fill up the textboxes.' )
	Lb.yview(tk.END)

	Lb.pack(side="left", fill="y")

	scrollbar.place(in_=Lb, relx=1.0, relheight=2.0, bordermode="outside")
	scrollbar.config( command = Lb.yview)
	scrollbar.pack(side="right", fill="y")


	link = tk.Label(root, text="Developed By : Md. Ashique Imran, under supervision of Md. Monowar Hossain for Banglalink Digital Communications Ltd. ", fg="white",bg=backgroundColor,font=sm_font, cursor="hand2",anchor='e')
	link.pack(pady=40,padx=2,side = 'right',fill='x')
	link.bind("<Button-1>", lambda event: webbrowser.open('https://github.com/AshiqueImran'))

	button1.config(command= lambda: fun(button1,resultLocation,Lb))
	resultLocation["state"] = "disable"


	root.title('Alarm Rectification Tool (Beta 2.2.6)')
	# root.wm_iconbitmap('logo.ico')
	root.geometry("1100x550") #You want the size of the app to be 500x500
	root.resizable(0, 0) #Don't allow resizing in the x or y direction
	root.configure(background=backgroundColor)
	# Positions the window in the center of the page.
	root.geometry("+"+str(50)+"+"+str(40))

	root.mainloop()