from tkinter import (Tk, StringVar, IntVar, Entry, Label, Button, Checkbutton, filedialog, END, messagebox)
from pyautogui import moveTo, click
from pynput.mouse import Listener
from pynput.mouse import Button as Btn
from datetime import datetime,timedelta
from time import sleep

positions = []
move_times = []
buttons = []

position_labels = []
delay_inputs = []
delays = []

recording = False
running = False

window = Tk()
window.title("Click recorder")
window.geometry('500x300')
window.rowconfigure(0,pad=30)
window.columnconfigure(0,weight=2)
window.columnconfigure(1,weight=4)
window.columnconfigure(2,weight=1)
window.columnconfigure(3,weight=2)
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
    if recording and pressed and (button == Btn.left or button == Btn.right):
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
    global running,delay_inputs
    b3_text.set("Running")
    window.update()
    running = True
    nr_points = len(positions)

    initial_delay = float(init_delay.get())
    sleep(initial_delay)
    click(x=positions[0][0],y=positions[0][1],button=buttons[0])

    i = 1
    while running:
        i = i % nr_points
        # try:
        moveDur = float(delay_inputs[(i-1) % nr_points].get())
        # except:
            # moveDur = float(default_delay.get())
        moveTo(positions[i][0],positions[i][1], duration=moveDur)
        click(button=buttons[i])
        i += 1

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

    rec_dur.set(1)
    last_delay = 0
    ts = datetime.fromtimestamp(0)
    for line in f:
        try:
            line = line.split()
            x = int(line[0]); y = int(line[1]); delay = float(line[2]); button = line[3]
            positions.append([x,y])
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


    make_inputs()
    delay_inputs[-1].delete(0,END)
    delay_inputs[-1].insert(0,last_delay)
    rec_dur.set(0)

def make_inputs():
    global position_labels, delay_inputs, delays

    j = len(position_labels)
    for i in range(j,len(positions)):
        p = positions[i]
        position_labels.append(Label(window,text = f"{buttons[i][0].upper()} x: {p[0]:<4} y: {p[1]:<4}"))
        position_labels[i].grid(column=0,row=i+2,sticky='w')

        delay_inputs.append(Entry(window))
        if  (i - j) < len(delays) - 1 and rec_dur.get():
            delay_inputs[i].insert(0,str((delays[i-j+1] - delays[i-j]).total_seconds() ) )
        else:
            delay_inputs[i].insert(0,default_delay.get())
        delay_inputs[i].grid(column=1,row=i+2)
    delays = []


record_button = Button(window,textvariable=b1_text, command = record_click)
record_button.grid(column=0,row=0)

reset_button = Button(window, text="Reset",command = reset_click)
reset_button.grid(column=2,row=0)

run_button = Button(window, textvariable=b3_text,command = run_click)
run_button.grid(column=1,row=0)

lbl = Label(window, text="Positions")
lbl.grid(column=0,row=1)

lbl2 = Label(window, text = "Click delay in s")
lbl2.grid(column=1,row=1)

chk1 = Checkbutton(window,text='Record\ndelays',variable=rec_dur)
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

save_button = Button(window, text="Save", command = save_click)
save_button.grid(column=3,row=5)

load_button = Button(window, text="Load", command = load_click)
load_button.grid(column=3,row=6)

window.mainloop()
