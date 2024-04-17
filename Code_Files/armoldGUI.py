import tkinter as tk
import customtkinter as ctk
from PIL import Image
from PIL import ImageTk
import os

class ArmoldGUI():
    def __init__(self):
        self.state = "idle"
        self.stateText = "Nothing in progress"
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
        for child in self.window.winfo_children():
            child.destroy()
        self.windowFrame = tk.Frame(self.window).pack()
        # recording area frames
        self.recordingsframeborder = tk.Frame(self.windowFrame, width=self.recordingsFrameWidth, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        self.recordingsframeborder.pack(side="left", expand=True, fill="both")
        self.recordingsframe = ctk.CTkFrame(self.recordingsframeborder, border_color="#BABFC9", fg_color="#BABFC9", border_width=self.borderPadding, corner_radius=15)
        self.recordingsframe.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # recording area elements
        self.statusAreaFrame = ctk.CTkFrame(self.recordingsframe, fg_color="#EAF1FF", bg_color="#BABFC9", border_width=0, corner_radius=15)
        self.statusAreaFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        self.statusMessage = tk.Label(self.statusAreaFrame, text=self.stateText, font=("Courier New Bold", 32), background="#EAF1FF")
        self.statusMessage.pack(side="left", padx=2*self.borderPadding, pady=2*self.borderPadding, expand=False, fill="both")
        self.recordingsList = ctk.CTkScrollableFrame(self.recordingsframe, bg_color="#BABFC9", fg_color="#BABFC9", scrollbar_fg_color="#FFFFFF", scrollbar_button_color="#5D6D8B", scrollbar_button_hover_color="#427FF6", corner_radius=15)
        self.recordingsList._scrollbar.configure(width=3*self.borderPadding, corner_radius=15)
        self.recordingsList.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        
        # controls area frames
        self.controlsframeborder = tk.Frame(self.windowFrame, width=self.controlsFrameWidth, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        self.controlsframeborder.pack(side="right", expand=False, fill="both")
        canvas = tk.Canvas(self.controlsframeborder, width=self.controlsFrameWidth, height=self.controlsFrameWidth, bd=0, highlightthickness=0, background="#FFFFFF")
        canvas.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        logoImg = Image.open("gui_icons/armold_logo_glow.png")
        logoImg = logoImg.resize((round(self.controlsFrameWidth),round(self.controlsFrameWidth)), Image.ANTIALIAS)
        canvas.logo = ImageTk.PhotoImage(logoImg)
        canvas.create_image(0, 0, anchor=tk.NW, image=canvas.logo)
        self.controlsframe = ctk.CTkFrame(self.controlsframeborder, width=self.controlsFrameWidth, fg_color="#BABFC9", corner_radius=15)
        self.controlsframe.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # controls area elements
        # record button
        recordButtonFrame = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#FFFFFF", corner_radius=15)
        recordButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.recordButtonMargin = tk.Frame(recordButtonFrame, width=self.controlsFrameWidth)
        self.recordButtonMargin.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        recordButtonImg = Image.open("gui_icons/record.png")
        if(self.state == "playback"):
            recordButtonImg = Image.open("gui_icons/no_record.png")
        recordButtonImg = recordButtonImg.resize((7*round(self.borderPadding),7*round(self.borderPadding)), Image.ANTIALIAS)
        recordButtonImage = ImageTk.PhotoImage(recordButtonImg)
        if(self.state == "recording"):
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="End Recording", font=("Courier New Bold", 32), text_color="#000000", fg_color="#EAF1FF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.stopRecording())
        elif(self.state == "playback"):
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier New Bold", 32), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
        else:
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier New Bold", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startRecording())
        self.recordButton.pack(side="left", expand=True, fill="both")
        self.recordButtonCanvas = tk.Canvas(recordButtonFrame, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
        self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
        if(self.state == "recording"):
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#427FF6", outline="#FFFFFF")
        else:
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        # mirror button
        mirrorButtonFrame = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#FFFFFF", corner_radius=15)
        mirrorButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.mirrorButtonMargin = tk.Frame(mirrorButtonFrame, width=self.controlsFrameWidth)
        self.mirrorButtonMargin.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        mirrorButtonImg = Image.open("gui_icons/mirror.png")
        if(self.state == "recording" or self.state == "playback"):
            mirrorButtonImg = Image.open("gui_icons/no_mirror.png")
        mirrorButtonImg = mirrorButtonImg.resize((7*round(self.borderPadding),7*round(self.borderPadding)), Image.ANTIALIAS)
        mirrorButtonImage = ImageTk.PhotoImage(mirrorButtonImg)
        if(self.state == "mirror"):
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Stop Control", font=("Courier New Bold", 32), text_color="#000000", fg_color="#EAF1FF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.stopMirror())
        elif(self.state == "recording" or self.state == "playback"):
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier New Bold", 32), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
        else:
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier New Bold", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startMirror())
        self.mirrorButton.pack(side="left", expand=True, fill="both")
        self.mirrorButtonCanvas = tk.Canvas(mirrorButtonFrame, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
        self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
        if(self.state == "mirror"):
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#427FF6", outline="#FFFFFF")
        else:
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        # debug and shutdown buttons
        tekButtonMargin = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#BABFC9", corner_radius=15)
        tekButtonMargin.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        debugButtonImg = Image.open("gui_icons/debug.png")
        debugButtonImg = debugButtonImg.resize((2*round(self.borderPadding),2*round(self.borderPadding)), Image.ANTIALIAS)
        debugButtonImage = ImageTk.PhotoImage(debugButtonImg)
        debugButton = ctk.CTkButton(tekButtonMargin, image=debugButtonImage, text="Open Debug Window", font=("Courier New Bold", 18), text_color="#000000", fg_color="#FFFFFF", bg_color="transparent", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.showDebugWindow())
        debugButton.pack(side="left")
        powerButtonImg = Image.open("gui_icons/power.png")
        powerButtonImg = powerButtonImg.resize((2*round(self.borderPadding),2*round(self.borderPadding)), Image.ANTIALIAS)
        powerButtonImage = ImageTk.PhotoImage(powerButtonImg)
        closeButton = ctk.CTkButton(tekButtonMargin, image=powerButtonImage, text="Shut Down", font=("Courier New Bold", 18), text_color="#000000", fg_color="#FFFFFF", bg_color="transparent", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.closeWindow())
        closeButton.pack(side="right")

        self.window.update()

    def startRecording(self):
        self.state = "recording"
        self.statetext = "Recording in progress"
        self.fillWindow()
        pass
    
    def stopRecording(self):
        self.state = "idle"
        self.statetext = "Nothing in progress"
        self.fillWindow()
        pass
    
    def startMirror(self):
        self.state = "mirror"
        self.statetext = "Mirroring motion"
        self.fillWindow()
        pass
    
    def stopMirror(self):
        self.state = "idle"
        self.statetext = "Nothing in progress"
        self.fillWindow()
        pass
    
    def showDebugWindow(self):
        pass
    
    def closeWindow(self):
        self.window.destroy()
        # os.system("sudo reboot")

armoldGUI = ArmoldGUI()
armoldGUI.window.mainloop()