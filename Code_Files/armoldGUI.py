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
        self.recordingsFrameWidth = 0.7 * self.screenwidth
        self.controlsFrameWidth = 0.3 * self.screenwidth
        self.borderPadding = 0.01 * self.screenheight
        self.window.geometry(f'{self.screenwidth}x{self.screenheight}+0+0')
        self.window.resizable(False, False)
        self.window.attributes('-fullscreen', True)
        self.window.protocol("WM_DELETE_WINDOW", lambda : self.closeWindow())
        self.fillWindow()

    def fillWindow(self):
        # recording area frames
        self.recordingsframeborder = tk.Frame(self.window, width=self.recordingsFrameWidth, highlightbackground="#BABFC9", highlightthickness=5)
        self.recordingsframeborder.pack(side="left", expand=True, fill="both")
        self.recordingsframe = tk.Frame(self.recordingsframeborder, background="#BABFC9")
        self.recordingsframe.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # recording area elements
        
        # controls area frames
        self.controlsframeborder = tk.Frame(self.window, width=self.controlsFrameWidth, highlightbackground="#BABFC9", highlightthickness=5)
        self.controlsframeborder.pack(side="right", expand=False, fill="both")
        canvas = tk.Canvas(self.controlsframeborder, width=self.controlsFrameWidth, height=self.controlsFrameWidth)
        canvas.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        img = Image.open("gui_icons/armold_logo_glow.png")
        img = img.resize((round(self.controlsFrameWidth),round(self.controlsFrameWidth)), Image.ANTIALIAS)
        canvas.logo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=canvas.logo)
        self.controlsframe = tk.Frame(self.controlsframeborder, width=self.controlsFrameWidth, background="#BABFC9")
        self.controlsframe.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # controls area elements
        self.recordButtonFrame = tk.Frame(self.controlsframe, width=self.controlsFrameWidth)
        self.recordButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.recordButton = tk.Button(self.recordButtonFrame, text="New Recording", command=lambda : self.closeWindow())
        tk.Shadow(self.recordButton, color='#ff0000', size=1.3)
        self.recordButton.pack(side="left")
        self.recordButtonCanvas = tk.Canvas(self.recordButtonFrame, width=4+3*self.borderPadding, height=4+3*self.borderPadding)
        self.recordButtonCanvas.pack(side="right", padx=self.borderPadding, expand=False, fill="none")
        self.recordButtonCanvas.create_oval(2,2, 3*self.borderPadding, 3*self.borderPadding, fill="#BABFC9", outline="#BABFC9")
        
        self.mirrorButtonFrame = tk.Frame(self.controlsframe, width=self.controlsFrameWidth)
        self.mirrorButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.mirrorButton = tk.Button(self.mirrorButtonFrame, text="Live Control", command=lambda : self.closeWindow())
        self.mirrorButton.pack(side="left")
        self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonFrame, width=4+3*self.borderPadding, height=4+3*self.borderPadding)
        self.mirrorButtonCanvas.pack(side="right", padx=self.borderPadding, expand=False, fill="none")
        self.mirrorButtonCanvas.create_oval(2,2, 3*self.borderPadding, 3*self.borderPadding, fill="#BABFC9", outline="#BABFC9")
        
        self.closeButton = tk.Button(self.controlsframe, text="Close Window", command=lambda : self.closeWindow())
        self.closeButton.pack(side="bottom")

        self.window.update()

    def closeWindow(self):
        self.window.destroy()
        # os.system("sudo reboot")

armoldGUI = ArmoldGUI()
armoldGUI.window.mainloop()