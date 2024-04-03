import tkinter as tk
from PIL import Image
from PIL import ImageTk
import os

class ArmoldGUI():
    def __init__(self):
        # window setup
        self.window = tk.Tk()
        self.window.title("Armold")
        self.screenwidth = self.window.winfo_screenwidth()
        self.screenheight = self.window.winfo_screenheight()
        self.window.geometry(f'{self.screenwidth}x{self.screenheight}+0+0')
        self.window.resizable(False, False)
        self.window.attributes('-fullscreen', True)
        self.window.protocol("WM_DELETE_WINDOW", lambda : self.closeWindow())
        self.fillWindow()

    def fillWindow(self):
        # frames
        self.recordingsframeborder = tk.Frame(self.window, width=0.7 * self.screenwidth, highlightbackground="#BABFC9", highlightthickness=5)
        self.recordingsframeborder.pack(side="left", expand=True, fill="both")
        self.recordingsframe = tk.Frame(self.recordingsframeborder, highlightbackground="#BABFC9", highlightthickness=10)
        self.recordingsframe.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        
        
        self.controlsframeborder = tk.Frame(self.window, width=0.3 * self.screenwidth, highlightbackground="#BABFC9", highlightthickness=5)
        self.controlsframeborder.pack(side="right", expand=False, fill="both")
        canvas = tk.Canvas(self.controlsframeborder)
        canvas.pack(side="top", padx=10, pady=10, expand=True, fill="both")
        img = Image.open("gui_icons/armold_logo_glow.png")
        img = img.resize((round(0.3 * self.screenwidth),round(0.3 * self.screenwidth)), Image.ANTIALIAS)
        canvas.test = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=canvas.test)
        self.controlsframe = tk.Frame(self.controlsframeborder, width=0.3 * self.screenwidth, highlightbackground="#BABFC9", highlightthickness=10)
        self.controlsframe.pack(side="bottom", padx=10, pady=10, expand=False, fill="x")

        # TODO (need actual questions) Form questions and boxes
        label1 = tk.Label(self.recordingsframe, text="Test Label 1").pack()

        # Form submit button
        submitButton = tk.Button(self.recordingsframe, text="Submit to SQL Server")
        submitButton.pack(side="bottom")
        
        closeButton = tk.Button(self.recordingsframe, text="Close Window", padx=30, pady=30, command=lambda : self.closeWindow())
        closeButton.pack(side="bottom")

        self.window.update()

    def closeWindow(self):
        self.window.destroy()
        # os.system("sudo reboot")

armoldGUI = ArmoldGUI()
armoldGUI.window.mainloop()