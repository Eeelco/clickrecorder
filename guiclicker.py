from tkinter import (Tk, StringVar, IntVar, Entry, Label, Button, Checkbutton)
from pyautogui import moveTo, click
import time
from pynput.mouse import Listener
from datetime import datetime

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

def on_click(x,y,button,pressed):
    if recording and pressed:
        if rec_dur.get():
            durations.append(datetime.now())
        positions.append([x,y])

def on_scroll(x,y,dx,dy):
    global running, b3_text
    running = False
    b3_text.set("Start")

listener = Listener(on_click=on_click,on_scroll=on_scroll)
listener.start()

b1_text.set("Start recording")
b3_text.set("Start")


def b1click():
    global recording
    if not recording:
        b1_text.set("Stop recording")
        recording = True
    else:
        positions.pop()
        if rec_dur.get():
            durations.pop()
        make_duration_inputs()
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
    b3_text.set("Start")
    b1_text.set("Start recording")
    window.update()

def b3click():
    global running,duration_inputs
    b3_text.set("Running")
    window.update()
    running = True
    i = 0
    n_els = len(positions)
    while running:
        i = i % n_els
        try:
            moveDur = float(duration_inputs[(i-1) % n_els].get())
        except:
            moveDur = 1
        moveTo(positions[i][0],positions[i][1], duration=moveDur)
        click()
        i += 1

def make_duration_inputs():
    global position_labels, duration_inputs
    for label in position_labels:
        label.grid_forget()
    for i in duration_inputs:
        i.grid_forget()
    position_labels = []
    duration_inputs = []
    for i in range(len(positions)):
        p = positions[i]
        position_labels.append(Label(window,text = "x: {} y: {}".format(p[0],p[1])))
        duration_inputs.append(Entry(window))
    for i,j in enumerate(position_labels):
        j.grid(column=0,row=i+2)
        duration_inputs[i].grid(column=1,row=i+2)
        if rec_dur.get() and i < len(durations) - 1:
            duration_inputs[i].insert(0,str((durations[i+1] - durations[i]).total_seconds() ) )


btn1 = Button(window,textvariable=b1_text, command = b1click)
btn1.grid(column=0,row=0)

btn2 = Button(window, text="Reset",command = b2click)
btn2.grid(column=1,row=0)

btn3 = Button(window, textvariable=b3_text,command = b3click)
btn3.grid(column=2,row=0)

lbl = Label(window, text="Positions")
lbl.grid(column=0,row=1)

lbl2 = Label(window, text = "Move duration in s\n(default = 1)")
lbl2.grid(column=1,row=1)

chk1 = Checkbutton(window,text='Record\ndurations',variable=rec_dur)
chk1.grid(column=3,row=0)

window.mainloop()
