from tkinter import (Tk, StringVar, IntVar, Entry, Label, Button, Checkbutton, filedialog, END, messagebox, Frame)
from pyautogui import moveTo, click
import pyautogui
from pynput.mouse import Listener
from pynput.mouse import Button as Btn
from datetime import datetime,timedelta
from time import sleep
from itertools import cycle
from bezier import random_bezier
import numpy as np

pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0

positions = []
move_times = []
buttons = []

position_labels = []
delay_inputs = []
delays = []

recording = False
running = False

window = Tk()
frame_left = Frame(window,padx=10,pady=10)
frame_left.grid(row=0,column=0)
frame_right = Frame(window,padx=10,pady=10)
frame_right.grid(row=0,column=1)
window.title("Click recorder")

frame_left.columnconfigure(0,minsize=120)
frame_left.columnconfigure(1,minsize=180)
frame_left.columnconfigure(2,minsize=50)
frame_left.rowconfigure(1,pad=20)
frame_left.grid(sticky='N')
frame_right.grid(sticky='N')

b1_text = StringVar(frame_left)
b3_text = StringVar(frame_left)
rec_dur = IntVar(frame_right)
human_like = IntVar(frame_right)
fixed_cycle_nr = IntVar(frame_right)
init_delay = StringVar(frame_right)
default_delay = StringVar(frame_right)

b1_text.set("Start recording")
b3_text.set("Start clicks")
init_delay.set("1")
default_delay.set("1")


def on_click(x,y,button,pressed):
    if recording and pressed and button in [Btn.left,Btn.right]:
        if rec_dur.get():
            delays.append(datetime.now())
        positions.append([x,y])
        buttons.append('left' if button == Btn.left else 'right')

def on_scroll(x,y,dx,dy):
    global running, b3_text
    running = False
    b3_text.set("Start clicks")

listener = Listener(on_click=on_click,on_scroll=on_scroll)
listener.start()


def record_click():
    global recording
    if not recording:
        b1_text.set("Stop recording")
        recording = True
    else:
        positions.pop()
        if rec_dur.get():
            delays.pop()
        make_inputs()
        b1_text.set("Start recording")
        recording = False

def reset_click():
    global recording, positions, running, position_labels, delay_inputs, delays, buttons
    for label in position_labels:
        label.grid_forget()
    for i in delay_inputs:
        i.grid_forget()
    positions = []
    delays = []
    position_labels = []
    delay_inputs = []
    buttons = []
    recording = False
    running = False
    b3_text.set("Start clicks")
    b1_text.set("Start recording")
    window.update()

def run_click():
    global running,delay_inputs,b3_text
    node_nr = 100
    nr_clicks = len(positions)
    b3_text.set("Running")
    if recording:
        record_click()
    window.update()
    running = True
    indices = cycle(range(nr_clicks))
    delays = [float(delay_inputs[i].get()) if delay_inputs[i].get() != '' else float(default_delay.get()) for i in range(len(positions))]
    delays = [delays[-1]] + delays[:-1]

    initial_delay = float(init_delay.get())
    sleep(initial_delay)
    click(x=positions[0][0],y=positions[0][1],button=buttons[0])

    j = 1
    if fixed_cycle_nr.get():
        j = int(fix_click_entry.get())

    next(indices)
    if not human_like.get():
        for i in indices:
            if not running or j < 1:
                running = False
                b3_text.set("Start clicks")
                break
            moveTo(positions[i][0],positions[i][1], duration=delays[i])
            click(button=buttons[i])
            if fixed_cycle_nr.get() and i == nr_clicks - 1:
                j -= 1
    else:
        for i in indices:
            if not running or j < 1:
                running = False
                b3_text.set("Start clicks")
                break
            target_pos = np.asarray(positions[i]) + np.random.randint(-1,2,size=2)
            curve, n_pts = random_bezier(np.asarray(pyautogui.position()), target_pos,0.2,node_nr)
            interval = (delays[i] + np.random.uniform(-0.1,0.1)) / n_pts
            for k in curve:
                sleep(interval)
                moveTo(k[0],k[1])
            click(button=buttons[i])
            if fixed_cycle_nr.get() and i == nr_clicks - 1:
                j -= 1

def save_click():
    outfile = filedialog.asksaveasfilename(title="Filename",filetypes=(("Click save files", "*.cls"),("all files","*")))
    with open(outfile,'w') as o:
        for i in range(len(positions)):
            o.write("{}\t{}\t{}\t{}\n".format(positions[i][0],positions[i][1],delay_inputs[i].get(),buttons[i]))

def load_click():
    global delay_inputs, delays, positions, buttons

    reset_button.invoke()
    infile = filedialog.askopenfilename(title="Filename",filetypes=(("Click save files", "*.cls"),("all files","*")))
    try:
        f = open(infile,'r').readlines()
    except:
        return

    last_delay = 0
    ts = datetime.fromtimestamp(0)
    for line in f:
        try:
            line = line.split()
            x = int(line[0]); y = int(line[1]); delay = float(line[2]); button = line[3]
            positions.append([x,y])
            assert button in ['left','right']
            buttons.append(button)
            if delays == []:
                delays.append(ts)
            else:
                delays.append(delays[-1] + timedelta(seconds=last_delay))
            last_delay = delay
        except:
            delays = []
            positions = []
            buttons = []
            messagebox.showerror(title='File load error', message = 'Error loading file')
            return


    rec_dur.set(1)
    make_inputs()
    rec_dur.set(0)
    delay_inputs[-1].delete(0,END)
    delay_inputs[-1].insert(0,last_delay)

def make_inputs():
    global position_labels, delay_inputs, delays

    j = len(position_labels)
    for i in range(j,len(positions)):
        p = positions[i]
        position_labels.append(Label(frame_left,text = f"{buttons[i][0].upper()} x: {p[0]:<4} y: {p[1]:<4}"))
        position_labels[i].grid(column=0,row=i+2,sticky='w')

        delay_inputs.append(Entry(frame_left))
        if  (i - j) < len(delays) - 1 and rec_dur.get():
            delay_inputs[i].insert(0,str((delays[i-j+1] - delays[i-j]).total_seconds() ) )
        else:
            delay_inputs[i].insert(0,default_delay.get())
        delay_inputs[i].grid(column=1,row=i+2,ipadx=5)
    delays = []


record_button = Button(frame_left,textvariable=b1_text, command = record_click)
record_button.grid(column=0,row=0)

reset_button = Button(frame_left, text="Reset",command = reset_click)
reset_button.grid(column=2,row=0)

run_button = Button(frame_left, textvariable=b3_text,command = run_click)
run_button.grid(column=1,row=0)

lbl = Label(frame_left, text="Clicks")
lbl.grid(column=0,row=1)

lbl2 = Label(frame_left, text = "Click delay in s")
lbl2.grid(column=1,row=1)

chk1 = Checkbutton(frame_right,text='Record\ndelays',variable=rec_dur)
chk1.grid(column=0,row=0,sticky='W')

chk2 = Checkbutton(frame_right,text='Human-like\nmovement',variable=human_like)
chk2.grid(column=0,row=1,sticky='W')

lbl3 = Label(frame_right,text="Initial delay in s")
lbl3.grid(column=0, row = 2)

init_delay_entry = Entry(frame_right,textvariable=init_delay,width=10)
init_delay_entry.grid(column=0,row=3)
def fill_ini(event=None):
    content = init_delay_entry.get()
    if content == '':
        init_delay_entry.insert(0,'1')
init_delay_entry.bind('<FocusOut>',fill_ini)

lbl4 = Label(frame_right,text="Default delay in s")
lbl4.grid(column=0, row = 4)

default_delay_entry = Entry(frame_right,textvariable=default_delay,width=10)
default_delay_entry.grid(column=0,row=5)
def fill_default(event=None):
    content = default_delay_entry.get()
    if content == '':
        default_delay_entry.insert(0,'1')
default_delay_entry.bind('<FocusOut>',fill_default)

fix_clicks = Checkbutton(frame_right,text='Fixed nr.\nof cycles',variable=fixed_cycle_nr)
fix_clicks.grid(column=0,row=6,sticky='W')
fix_click_entry = Entry(frame_right,width=10)
fix_click_entry.grid(column=0,row=7)


save_button = Button(frame_right, text="Save", command = save_click)
save_button.grid(column=0,row=8,pady=5)

load_button = Button(frame_right, text="Load", command = load_click)
load_button.grid(column=0,row=9)

window.mainloop()
