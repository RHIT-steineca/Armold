import tkinter as tk
import customtkinter as ctk
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
        self.recordingsframeborder = tk.Frame(self.window, width=self.recordingsFrameWidth, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        self.recordingsframeborder.pack(side="left", expand=True, fill="both")
        self.recordingsframe = ctk.CTkFrame(self.recordingsframeborder, border_color="#BABFC9", border_width=self.borderPadding, corner_radius=15)
        self.recordingsframe.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # recording area elements
        self.recordingsList = ctk.CTkScrollableFrame(self.recordingsframe, bg_color="#BABFC9", fg_color="#BABFC9", scrollbar_fg_color="#FFFFFF", scrollbar_button_color="#5D6D8B", scrollbar_button_hover_color="#427FF6", corner_radius=15)
        self.recordingsList.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # controls area frames
        self.controlsframeborder = tk.Frame(self.window, width=self.controlsFrameWidth, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        self.controlsframeborder.pack(side="right", expand=False, fill="both")
        canvas = tk.Canvas(self.controlsframeborder, width=self.controlsFrameWidth, height=self.controlsFrameWidth, bd=0, highlightthickness=0, background="#FFFFFF")
        canvas.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        img = Image.open("gui_icons/armold_logo_glow.png")
        img = img.resize((round(self.controlsFrameWidth),round(self.controlsFrameWidth)), Image.ANTIALIAS)
        canvas.logo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=canvas.logo)
        self.controlsframe = ctk.CTkFrame(self.controlsframeborder, width=self.controlsFrameWidth, fg_color="#BABFC9", corner_radius=15)
        self.controlsframe.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # controls area elements
        recordButtonFrame = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#FFFFFF", corner_radius=15)
        recordButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.recordButtonMargin = tk.Frame(recordButtonFrame, width=self.controlsFrameWidth)
        self.recordButtonMargin.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.recordButton = ctk.CTkButton(self.recordButtonMargin, text="New Recording", font=("Courier New Bold", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startRecording())
        self.recordButton.pack(side="left", expand=True, fill="both")
        self.recordButtonCanvas = tk.Canvas(recordButtonFrame, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
        self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
        self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        
        mirrorButtonFrame = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#FFFFFF", corner_radius=15)
        mirrorButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.mirrorButtonMargin = tk.Frame(mirrorButtonFrame, width=self.controlsFrameWidth)
        self.mirrorButtonMargin.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, text="Live Control", font=("Courier New Bold", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startMirror())
        self.mirrorButton.pack(side="left", expand=True, fill="both")
        self.mirrorButtonCanvas = tk.Canvas(mirrorButtonFrame, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
        self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
        self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        
        tekButtonMargin = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#BABFC9", corner_radius=15)
        tekButtonMargin.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        debugButton = ctk.CTkButton(tekButtonMargin, text="Open Debug Window", font=("Courier New Bold", 18), text_color="#000000", fg_color="#FFFFFF", bg_color="transparent", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.showDebugWindow())
        debugButton.pack(side="left")
        closeButton = ctk.CTkButton(tekButtonMargin, text="Shut Down", font=("Courier New Bold", 18), text_color="#000000", fg_color="#FFFFFF", bg_color="transparent", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.closeWindow())
        closeButton.pack(side="right")

        self.window.update()

    def startRecording(self):
        pass
    
    def stopRecording(self):
        pass
    
    def startMirror(self):
        pass
    
    def stopMirror(self):
        pass
    
    def showDebugWindow(self):
        pass
    
    def closeWindow(self):
        self.window.destroy()
        # os.system("sudo reboot")

armoldGUI = ArmoldGUI()
armoldGUI.window.mainloop()