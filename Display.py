import sys
import UHPy
from tkinter import *

uhand = UHPy.UH()

root = Tk()

root.option_add("font",("FixedSys",14))
root.geometry("400x400")



buff = StringVar()
buff.set("")

Label(textvariable = buff).pack()

def show_UHPR():
    uhand.updatePhotosensors()
    buff.set(uhand.UHPR)
    root.after(1,show_UHPR)

show_UHPR()
root.mainloop()
