import sys
from UHPy import *
from tkinter import *

uhand = UH()

root = Tk()

root.option_add("font",("FixedSys",14))
root.geometry("400x400")
root.title("Unlimitedhand")



PR = StringVar()
#PR.set("")

Angle = StringVar()
#Angle.set("")

UHGyroAccel = StringVar()
#UHGyroAccel.set("")

Test = StringVar()

Label(textvariable = "PhotoReflector").pack()
Label(textvariable = PR).pack()
Label(textvariable = "Angle").pack()
Label(textvariable = Angle).pack()
Label(textvariable = "GyroAccel").pack()
Label(textvariable = UHGyroAccel).pack()
Label(textvariable = Test).pack()

DataCollectionButton = Button(text="ジェスチャデータ収集")
DataCollectionButton.bind("<Button-1>",uhand.gestureDataCollection)
GestureClassifierMake = Button(text="識別器作成")
GestureClassifierMake.bind("<Button-1>",uhand.gestureLogisticClassifier)

DataCollectionButton.pack()
GestureClassifierMake.pack()

nowGesture = StringVar()

alphabet = ["a","b","c","d","e","f","g","h"]

def show_UHPR():
    uhand.updatePhotosensors()
    uhand.updateAngle()
    uhand.updateUH3DGyroAccel()
    uhand.updateAnglePR()

    PR.set(uhand.UHPR)
    Angle.set(uhand.UHAngle)
    UHGyroAccel.set(uhand.UHGyroAccelData)

    nowGesture.set(uhand.nowGesture)
    Label(textvariable = "PhotoReflector").pack()

    if uhand.UHPR[0] > 0:
        if uhand.charCount < len(alphabet)-1:
            uhand.charCount += 1
            Test.set(alphabet[uhand.charCount])
        
    else:
        if uhand.charCount >= 0:
            uhand.charCount -= 1
            Test.set(alphabet[uhand.charCount])

    root.after(1,show_UHPR)

show_UHPR()
root.mainloop()
