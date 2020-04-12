from tkinter import (Tk, StringVar, IntVar, Entry, Label, Button, Checkbutton)
from pyautogui import moveTo, click
from pynput.mouse import Listener
from datetime import datetime
from time import sleep

positions = []
move_times = []

position_labels = []
duration_inputs = []
durations = []

recording = False
running = False

window = Tk()
window.title("Click recorder")
window.geometry('500x300')
window.rowconfigure(0,pad=30)
window.columnconfigure(0,weight=2)
window.columnconfigure(1,weight=4)
window.columnconfigure(2,weight=1)
window.columnconfigure(3,weight=1)
b1_text = StringVar(window)
b3_text = StringVar(window)
rec_dur = IntVar(window)
init_delay = StringVar(window)
default_delay = StringVar(window)

b1_text.set("Start recording")
b3_text.set("Start clicks")
init_delay.set("1")
default_delay.set("1")


def on_click(x,y,button,pressed):
    if recording and pressed:
        if rec_dur.get():
            durations.append(datetime.now())
        positions.append([x,y])

def on_scroll(x,y,dx,dy):
    global running, b3_text
    running = False
    b3_text.set("Start clicks")

listener = Listener(on_click=on_click,on_scroll=on_scroll)
listener.start()


def b1click():
    global recording
    if not recording:
        b1_text.set("Stop recording")
        recording = True
    else:
        positions.pop()
        if rec_dur.get():
            durations.pop()
        make_inputs()
        b1_text.set("Start recording")
        recording = False

def b2click():
    global recording, positions, running, position_labels, duration_inputs, durations
    positions = []
    durations = []
    for label in position_labels:
        label.grid_forget()
    for i in duration_inputs:
        i.grid_forget()
    recording = False
    running = False
    b3_text.set("Start clicks")
    b1_text.set("Start recording")
    window.update()

def b3click():
    global running,duration_inputs
    b3_text.set("Running")
    window.update()
    running = True
    nr_points = len(positions)

    initial_delay = float(init_delay.get())
    sleep(initial_delay)
    click(x=positions[0][0],y=positions[0][1])

    i = 1
    while running:
        i = i % nr_points
        try:
            moveDur = float(duration_inputs[(i-1) % nr_points].get())
        except:
            moveDur = float(default_delay.get())
        moveTo(positions[i][0],positions[i][1], duration=moveDur)
        click()
        i += 1

def make_inputs():
    global position_labels, duration_inputs, durations

    j = len(position_labels)
    for i in range(j,len(positions)):
        p = positions[i]
        position_labels.append(Label(window,text = "x: {} y: {}".format(p[0],p[1])))
        position_labels[i].grid(column=0,row=i+2)

        duration_inputs.append(Entry(window))
        if  (i - j) < len(durations) - 1 and rec_dur.get():
            duration_inputs[i].insert(0,str((durations[i-j+1] - durations[i-j]).total_seconds() ) )
        else:
            duration_inputs[i].insert(0,default_delay.get())
        duration_inputs[i].grid(column=1,row=i+2)
    durations = []


btn1 = Button(window,textvariable=b1_text, command = b1click)
btn1.grid(column=0,row=0)

btn2 = Button(window, text="Reset",command = b2click)
btn2.grid(column=2,row=0)

btn3 = Button(window, textvariable=b3_text,command = b3click)
btn3.grid(column=1,row=0)

lbl = Label(window, text="Positions")
lbl.grid(column=0,row=1)

lbl2 = Label(window, text = "Click delay in s")
lbl2.grid(column=1,row=1)

chk1 = Checkbutton(window,text='Record\ndurations',variable=rec_dur)
chk1.grid(column=3,row=0)

lbl3 = Label(window,text="Initial delay in s")
lbl3.grid(column=3, row = 1)

init_delay_entry = Entry(window,textvariable=init_delay)
init_delay_entry.grid(column=3,row=2)
def fill_ini(event=None):
    content = init_delay_entry.get()
    if content == '':
        init_delay_entry.insert(0,'1')
init_delay_entry.bind('<FocusOut>',fill_ini)

lbl4 = Label(window,text="Default delay in s")
lbl4.grid(column=3, row = 3)

default_delay_entry = Entry(window,textvariable=default_delay)
default_delay_entry.grid(column=3,row=4)
def fill_default(event=None):
    content = default_delay_entry.get()
    if content == '':
        default_delay_entry.insert(0,'1')
default_delay_entry.bind('<FocusOut>',fill_default)

window.mainloop()
