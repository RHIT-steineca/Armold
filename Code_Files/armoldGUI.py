import tkinter as tk
import customtkinter as ctk
from PIL import Image
from PIL import ImageTk
import math
import os

brain = tk.Tk()
testval = brain
brain.timeline = ["a", "b", "c"]
brain.originalRate = 1
brain.recordedMovements = {"test_1":testval,"test_2":testval,"test_3":testval,"test_4":testval,"test_5":testval,"test_6":testval,"test_7":testval}

class ArmoldGUI():
    def __init__(self):
        self.state = "disabled"
        self.stateText = "Armold is awake! \nNow looking for its arm..."
        self.playing = "NONE"
        self.playbackLoop = False
        # window setup
        self.window = brain
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
        self.windowFrame = tk.Frame(self.window).pack()
        # recording area frames
        self.recordingsframeborder = tk.Frame(self.windowFrame, width=self.recordingsFrameWidth, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        self.recordingsframeborder.pack(side="left", expand=True, fill="both")
        self.recordingsframe = ctk.CTkFrame(self.recordingsframeborder, border_color="#BABFC9", fg_color="#BABFC9", border_width=self.borderPadding, corner_radius=15)
        self.recordingsframe.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # recording area elements
        self.statusAreaFrame = ctk.CTkFrame(self.recordingsframe, fg_color="#EAF1FF", bg_color="#BABFC9", border_width=0, corner_radius=15)
        self.statusAreaFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        self.recordingsList = ctk.CTkScrollableFrame(self.recordingsframe, bg_color="#BABFC9", fg_color="#BABFC9", scrollbar_fg_color="#FFFFFF", scrollbar_button_color="#5D6D8B", scrollbar_button_hover_color="#427FF6", corner_radius=15)
        self.recordingsList._scrollbar.configure(width=10*self.borderPadding, corner_radius=30)
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
        self.recordButtonFrame = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#FFFFFF", corner_radius=15)
        self.recordButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.recordButtonMargin = tk.Frame(self.recordButtonFrame, width=self.controlsFrameWidth, background="#FFFFFF")
        self.recordButtonMargin.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # mirror button
        self.mirrorButtonFrame = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#FFFFFF", corner_radius=15)
        self.mirrorButtonFrame.pack(side="top", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        self.mirrorButtonMargin = tk.Frame(self.mirrorButtonFrame, width=self.controlsFrameWidth, background="#FFFFFF")
        self.mirrorButtonMargin.pack(side="left", padx=self.borderPadding, pady=self.borderPadding, expand=True, fill="both")
        # debug and shutdown buttons
        tekButtonMargin = ctk.CTkFrame(self.controlsframe, width=self.controlsFrameWidth, fg_color="#BABFC9", corner_radius=15)
        tekButtonMargin.pack(side="bottom", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
        debugButtonImage = ctk.CTkImage(Image.open("gui_icons/debug.png"), size=(2*round(self.borderPadding),2*round(self.borderPadding)))
        debugButton = ctk.CTkButton(tekButtonMargin, image=debugButtonImage, text="Open Debug Window", font=("Courier New Bold", 18), text_color="#000000", fg_color="#FFFFFF", bg_color="transparent", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.showDebugWindow())
        debugButton.pack(side="left")
        powerButtonImage = ctk.CTkImage(Image.open("gui_icons/power.png"), size=(2*round(self.borderPadding),2*round(self.borderPadding)))
        closeButton = ctk.CTkButton(tekButtonMargin, image=powerButtonImage, text="Shut Down", font=("Courier New Bold", 18), text_color="#000000", fg_color="#FFFFFF", bg_color="transparent", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.closeWindow())
        closeButton.pack(side="right")

        self.updateGraphics()
        
    def updateGraphics(self):
        # clear old state-dependent graphics
        for child in self.statusAreaFrame.winfo_children() + self.recordingsList.winfo_children() + self.recordButtonMargin.winfo_children() + self.mirrorButtonMargin.winfo_children():
            child.destroy()
        
        # set status message
        self.statusMessage = tk.Label(self.statusAreaFrame, text=self.stateText, font=("Courier New Bold", 32), background="#EAF1FF", justify="left")
        self.statusMessage.pack(side="left", padx=2*self.borderPadding, pady=2*self.borderPadding, expand=False, fill="both")
        
        if(self.state == "idle"):
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#FFFFFF", bg_color="#BABFC9", corner_radius=15)
                playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier New Bold", 32), text_color="#000000", justify="left")
                nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#DDDDDD", bg_color="#FFFFFF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15)
                playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier New Bold", 32), text_color="#000000")
                durationLabel.pack(side="right")
                playButtonImage = ctk.CTkImage(Image.open("gui_icons/play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#DDDDDD", hover_color="#EAF1FF", corner_radius=15, command=lambda name=name: self.startPlayback(name))
                playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#DDDDDD", hover_color="#EAF1FF", corner_radius=15, command=lambda name=name: self.deleteRecording(name))
                deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier New Bold", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startRecording())
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier New Bold", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startMirror())
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        elif(self.state == "mirror"):
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#FFFFFF", bg_color="#BABFC9", corner_radius=15)
                playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier New Bold", 32), text_color="#000000", justify="left")
                nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#DDDDDD", bg_color="#FFFFFF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15)
                playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier New Bold", 32), text_color="#000000")
                durationLabel.pack(side="right")
                playButtonImage = ctk.CTkImage(Image.open("gui_icons/play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#DDDDDD", hover_color="#EAF1FF", corner_radius=15, command=lambda name=name: self.startPlayback(name))
                playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#DDDDDD", hover_color="#EAF1FF", corner_radius=15, command=lambda name=name: self.deleteRecording(name))
                deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier New Bold", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.startRecording())
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Stop Control", font=("Courier New Bold", 32), text_color="#000000", fg_color="#EAF1FF", bg_color="#FFFFFF", hover_color="#EAF1FF", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.stopMirror())
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#427FF6", outline="#FFFFFF")
        elif(self.state == "playback"):
            # duration and loop buttons
            self.loopButtonMargin = tk.Frame(self.statusAreaFrame, width=self.controlsFrameWidth, background="#EAF1FF")
            self.loopButtonMargin.pack(side="right", padx=self.borderPadding, pady=self.borderPadding, expand=False, fill="both")
            self.playbackDuration = tk.Label(self.loopButtonMargin, text="0:00\n/0:00", font=("Courier New Bold", 20), background="#EAF1FF", bd=0, highlightthickness=0, justify="right")
            self.playbackDuration.pack(side="left", expand=True, fill="both", padx=self.borderPadding)
            loopButtonImage = ctk.CTkImage(Image.open("gui_icons/loop.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            if(self.playbackLoop == True):
                self.loopButton = ctk.CTkButton(self.loopButtonMargin, image=loopButtonImage, text="Loop", font=("Courier New Bold", 32), text_color="#FFB800", fg_color="#FFD9A0", bg_color="#EAF1FF", hover_color="#FFD9A0", border_color="#FFB800", border_width=self.borderPadding, corner_radius=15, command=lambda : self.toggleLoop())
            else:
                self.loopButton = ctk.CTkButton(self.loopButtonMargin, image=loopButtonImage, text="Loop", font=("Courier New Bold", 32), text_color="#000000", fg_color="#FFFFFF", bg_color="#EAF1FF", hover_color="#FFD9A0", border_color="#DDDDDD", border_width=self.borderPadding, corner_radius=15, command=lambda : self.toggleLoop())
            self.loopButton.pack(side="right", expand=False, fill="both")
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                if(name == self.playing):
                    playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#EAF1FF", bg_color="#BABFC9", corner_radius=15)
                    playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                    nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier New Bold", 32), text_color="#000000", justify="left")
                    nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                    playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#BDBDBD", bg_color="#EAF1FF", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
                    playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                    durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier New Bold", 32), text_color="#000000")
                    durationLabel.pack(side="right")
                    stopButtonImage = ctk.CTkImage(Image.open("gui_icons/stop.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                    stopButton = ctk.CTkButton(playbackButtonsFrame, image=stopButtonImage, width=7*round(self.borderPadding), text="", fg_color="#FFFFFF", bg_color="#BDBDBD", hover_color="#EAF1FF", corner_radius=15, command=lambda : self.stopPlayback())
                    stopButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                    deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/no_delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                    deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                    deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                else:
                    playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#DADADA", bg_color="#BABFC9", corner_radius=15)
                    playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                    nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier New Bold", 32), text_color="#BDBDBD", justify="left")
                    nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                    playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#BDBDBD", bg_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
                    playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                    durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier New Bold", 32), text_color="#BDBDBD")
                    durationLabel.pack(side="right")
                    playButtonImage = ctk.CTkImage(Image.open("gui_icons/no_play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                    playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                    playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                    deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/no_delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                    deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                    deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/no_record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier New Bold", 32), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/no_mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier New Bold", 32), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        elif(self.state == "recording"):
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#DADADA", bg_color="#BABFC9", corner_radius=15)
                playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier New Bold", 32), text_color="#BDBDBD", justify="left")
                nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#BDBDBD", bg_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
                playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier New Bold", 32), text_color="#BDBDBD")
                durationLabel.pack(side="right")
                playButtonImage = ctk.CTkImage(Image.open("gui_icons/no_play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/no_delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/no_record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier New Bold", 32), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/no_mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier New Bold", 32), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        elif(self.state == "disabled"):
            # playback buttons
            for rn, rec in brain.recordedMovements.items():
                name = rn.replace("_", " ")
                durationsecs = math.floor(len(rec.timeline) * (1.0 / rec.originalRate))
                displaysecs = durationsecs%60
                if(displaysecs < 10):
                    displaysecs = f"0{displaysecs}"
                duration = f"{math.floor(durationsecs/60)}:{displaysecs}"
                playbackFrame = ctk.CTkFrame(self.recordingsList, fg_color="#DADADA", bg_color="#BABFC9", corner_radius=15)
                playbackFrame.pack(side="top", expand=False, fill="x", padx=(0,self.borderPadding), pady=self.borderPadding)
                nameLabel = ctk.CTkLabel(playbackFrame, text=name, font=("Courier New Bold", 32), text_color="#BDBDBD", justify="left")
                nameLabel.pack(side="left", expand=False, fill="x", padx=self.borderPadding, pady=self.borderPadding)
                playbackButtonsFrame = ctk.CTkFrame(playbackFrame, fg_color="#BDBDBD", bg_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
                playbackButtonsFrame.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                durationLabel = ctk.CTkLabel(playbackFrame, text=duration, font=("Courier New Bold", 32), text_color="#BDBDBD")
                durationLabel.pack(side="right")
                playButtonImage = ctk.CTkImage(Image.open("gui_icons/no_play.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                playButton = ctk.CTkButton(playbackButtonsFrame, image=playButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                playButton.pack(side="left", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
                deleteButtonImage = ctk.CTkImage(Image.open("gui_icons/no_delete.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
                deleteButton = ctk.CTkButton(playbackButtonsFrame, image=deleteButtonImage, width=7*round(self.borderPadding), text="", fg_color="#DADADA", bg_color="#BDBDBD", hover_color="#DADADA", corner_radius=15)
                deleteButton.pack(side="right", expand=False, fill="none", padx=self.borderPadding, pady=self.borderPadding)
            # record button
            recordButtonImage = ctk.CTkImage(Image.open("gui_icons/no_record.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.recordButton = ctk.CTkButton(self.recordButtonMargin, image=recordButtonImage, text="New Recording", font=("Courier New Bold", 32), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.recordButton.pack(side="left", expand=True, fill="both")
            self.recordButtonCanvas = tk.Canvas(self.recordButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.recordButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.recordButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
            # mirror button
            mirrorButtonImage = ctk.CTkImage(Image.open("gui_icons/no_mirror.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
            self.mirrorButton = ctk.CTkButton(self.mirrorButtonMargin, image=mirrorButtonImage, text="Live Control", font=("Courier New Bold", 32), text_color="#BDBDBD", fg_color="#DADADA", bg_color="#DADADA", hover_color="#DADADA", border_color="#BDBDBD", border_width=self.borderPadding, corner_radius=15)
            self.mirrorButton.pack(side="left", expand=True, fill="both")
            self.mirrorButtonCanvas = tk.Canvas(self.mirrorButtonMargin, width=3*self.borderPadding, height=3*self.borderPadding, bd=0, highlightthickness=0, background="#FFFFFF")
            self.mirrorButtonCanvas.pack(side="right", padx=(self.borderPadding, 2*self.borderPadding), expand=False, fill="none")
            self.mirrorButtonCanvas.create_oval(0,0,3*self.borderPadding,3*self.borderPadding, fill="#BABFC9", outline="#FFFFFF")
        # update window with new graphics
        self.window.update()

    def startRecording(self):
        self.state = "recording"
        self.stateText = "Recording in progress\n"
        self.updateGraphics()
        pass
    
    def stopRecording(self):
        self.state = "idle"
        self.stateText = "Nothing in progress\n"
        for child in self.window.winfo_children():
            child.destroy()
        self.windowFrame = tk.Frame(self.window).pack()
        recordingframeborder = tk.Frame(self.windowFrame, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        recordingframeborder.pack(side="top", expand=True, fill="both")
        recordingInfoLabelBorder = tk.Frame(recordingframeborder, background="#FFFFFF", height=0.25*self.screenheight)
        recordingInfoLabelBorder.pack(side="top", expand=False, fill="both", padx=self.borderPadding, pady=(0.25*self.screenheight,self.borderPadding))
        infoLabel = ctk.CTkLabel(recordingInfoLabelBorder, text="Nice! Your recording is complete...\nWhat did you just teach Armold to do?", font=("Courier New Bold", 52), text_color="#000000")
        infoLabel.pack(side="top", expand=False, fill="both")
        recordingEntriesBorder = tk.Frame(recordingframeborder, background="#FFFFFF", height=0.1*self.screenheight)
        recordingEntriesBorder.pack(side="top", expand=False, fill="both", padx=5*self.borderPadding, pady=self.borderPadding)
        recordingName = tk.StringVar()
        recordingNameEntry = ctk.CTkEntry(recordingEntriesBorder, textvariable=recordingName, placeholder_text="", font=("Courier New Bold", 32), text_color="#000000", fg_color="#EAF1FF", bg_color="#FFFFFF", border_color="#5D6D8B", border_width=self.borderPadding, corner_radius=15)
        recordingNameEntry.pack(side="left", expand=True, fill="both")
        recordingName.trace_add("write", lambda *args: recordingNameEntry.delete(25))
        cancelImage = ctk.CTkImage(Image.open("gui_icons/cancel.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
        cancelButton = ctk.CTkButton(recordingEntriesBorder, image=cancelImage, text="Cancel", font=("Courier New Bold", 32), text_color="#842C2C", fg_color="#F64242", bg_color="#FFFFFF", hover_color="#F64242", border_color="#842C2C", border_width=self.borderPadding, corner_radius=15, command=lambda : self.cancelRecording())
        cancelButton.pack(side="right", expand=False, fill="both")
        acceptImage = ctk.CTkImage(Image.open("gui_icons/accept.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
        acceptButton = ctk.CTkButton(recordingEntriesBorder, image=acceptImage, text="Accept", font=("Courier New Bold", 32), text_color="#34B801", fg_color="#42F65E", bg_color="#FFFFFF", hover_color="#42F65E", border_color="#34B801", border_width=self.borderPadding, corner_radius=15, command=lambda : self.acceptRecording(recordingName.get()))
        acceptButton.pack(side="right", expand=False, fill="both")
        self.window.update()
        recordingNameEntry.focus_force()
    
    def acceptRecording(self, name):
        # TODO save recording data
        for child in self.window.winfo_children():
            child.destroy()
        self.fillWindow()
    
    def cancelRecording(self):
        for child in self.window.winfo_children():
            child.destroy()
        self.fillWindow()
    
    def startMirror(self):
        self.state = "mirror"
        self.stateText = "Live control in progress\n"
        self.updateGraphics()
        pass
    
    def stopMirror(self):
        self.state = "idle"
        self.stateText = "Nothing in progress\n"
        self.updateGraphics()
        pass
    
    def startPlayback(self, name):
        self.state = "playback"
        self.stateText = f"Playing\n{name}"
        self.playing = name
        self.updateGraphics()
        pass
    
    def stopPlayback(self):
        self.state = "idle"
        self.stateText = "Nothing in progress\n"
        self.playing = "NONE"
        self.updateGraphics()
        pass
    
    def deleteRecording(self, name):
        for child in self.window.winfo_children():
            child.destroy()
        self.windowFrame = tk.Frame(self.window).pack()
        recordingframeborder = tk.Frame(self.windowFrame, background="#FFFFFF", highlightbackground="#BABFC9", highlightthickness=5)
        recordingframeborder.pack(side="top", expand=True, fill="both")
        recordingInfoLabelBorder = tk.Frame(recordingframeborder, background="#FFFFFF")
        recordingInfoLabelBorder.pack(side="top", expand=False, fill="both", padx=self.borderPadding, pady=(0.25*self.screenheight,self.borderPadding))
        infoLabel = ctk.CTkLabel(recordingInfoLabelBorder, text=f"Are you sure that you want to\ndelete the recording\n{name}?", font=("Courier New Bold", 52), text_color="#000000")
        infoLabel.pack(side="top", expand=False, fill="both")
        recordingEntriesBorder = tk.Frame(recordingframeborder, background="#FFFFFF")
        recordingEntriesBorder.pack(side="top", expand=False, fill="both", padx=5*self.borderPadding, pady=5*self.borderPadding)
        acceptImage = ctk.CTkImage(Image.open("gui_icons/accept.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
        acceptButton = ctk.CTkButton(recordingEntriesBorder, image=acceptImage, text="Accept", font=("Courier New Bold", 32), text_color="#34B801", fg_color="#42F65E", bg_color="#FFFFFF", hover_color="#42F65E", border_color="#34B801", border_width=self.borderPadding, corner_radius=15, command=lambda : self.acceptDelete(name))
        acceptButton.pack(side="left", expand=True, fill="both", padx=5*self.borderPadding)
        cancelImage = ctk.CTkImage(Image.open("gui_icons/cancel.png"), size=(7*round(self.borderPadding),7*round(self.borderPadding)))
        cancelButton = ctk.CTkButton(recordingEntriesBorder, image=cancelImage, text="Cancel", font=("Courier New Bold", 32), text_color="#842C2C", fg_color="#F64242", bg_color="#FFFFFF", hover_color="#F64242", border_color="#842C2C", border_width=self.borderPadding, corner_radius=15, command=lambda : self.cancelRecording())
        cancelButton.pack(side="right", expand=True, fill="both", padx=5*self.borderPadding)
        self.window.update()
    
    def acceptDelete(self, name):
        # TODO delete recording data
        for child in self.window.winfo_children():
            child.destroy()
        self.fillWindow()
    
    def toggleLoop(self):
        self.playbackLoop = not self.playbackLoop
        self.updateGraphics()
        
    def updatePlaybackDuration(self, val):
        self.playbackDuration.configure(text=val)
        self.playbackDuration.update()
    
    def showDebugWindow(self):
        pass
    
    def closeWindow(self):
        self.window.destroy()
        # os.system("sudo reboot")

armoldGUI = ArmoldGUI()
armoldGUI.window.mainloop()