import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image


def left_button(root, index_list):
    index_list.append(0)
    root.destroy()


def right_button(root, index_list):
    index_list.append(1)
    root.destroy()


def open_label_window(img_path, index_list):
    # create main window
    root = tk.Tk()
    # Open window with title and dimensions:
    root.title("Pairwise Comparison Labelling")
    root.geometry('1000x800')
    # add button widget
    btn_left = Button(root, text='1', bd='5', command=lambda: left_button(root, index_list))
    btn_right = Button(root, text='2', bd='5', command=lambda: right_button(root, index_list))
    # Set the position of button
    btn_left.place(x=420, y=700)
    btn_right.place(x=520, y=700)
    # add option of labelling with keyboard
    root.bind("a", lambda event: left_button(root, index_list))
    root.bind("b", lambda event: right_button(root, index_list))
    # Create a photoimage object of the image in the path
    img = Image.open(img_path)
    im = ImageTk.PhotoImage(img)
    # add label widget to display image
    label = tk.Label(image=im)
    label.image = im
    # Position image
    label.place(relx=0.5, rely=0.5, anchor=CENTER)
    root.mainloop()


