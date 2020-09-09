#!/usr/bin/env python
# coding: utf-8

# In[1]:

"""BEAT PLAYER"""
# import
import os
import time
import mutagen
from tkinter import *
from pygame import mixer
from tkinter import filedialog
from mutagen.mp3 import MP3
from pathlib import Path

# define main frame
master = Tk()
master.title("Beat Player")
mixer.init()

master.configure(bg='#383859')

"""SCREEN POSITION/SIZE SETTINGS"""
# get screen width and height
screen_width = master.winfo_screenwidth()
screen_height = master.winfo_screenheight()

# calculate position x and y coordinates
x = (screen_width/2) - (336)
y = (screen_height/2) - (300/2)

# set original size
master.geometry('%dx%d+%d+%d' % (844, 170, x, y)) 

# resize min/max
master.minsize(width=844, height=170)
master.maxsize(width=844, height=170)


"""DEFINE VARIABLES"""
resetPlayer = ""
songInLoop = False
absolutPath = ""
songDirDict = {} 
mins = 0
secs = 0
status = StringVar()
status.set("-")


def deleteSong():
    """Delete selected song('s) from playlist"""  
    # deletes the selected song(s) in reverse order so that songs earlier in the list are not reindexed by delete
    selectedSongs = lb.curselection()
    for song in selectedSongs[::-1]:
        lb.delete(song)
              
              
def playSong():
    global absolutPath, playingSongIndex, status
    if status.get() == ("-Paused"):
        mixer.music.unpause()
        status.set("-Playing")
        playBtn['image'] = pauseImg 
        getSongInfo()
    elif status.get() == ("-Playing"):
        mixer.music.pause()
        status.set("-Paused")
        playBtn['image'] = playImg
    elif status.get() == ("-"):
        playingSongIndex = lb.index(ACTIVE)
        songTitle=lb.get(ACTIVE) #[:-6]
        absolutPath = songDirDict[songTitle] + "\\" + songTitle
        # Displaying Status
        status.set("-Playing")
        # Load Selected Song
        mixer.music.load(absolutPath)
        # Play Selected Song
        mixer.music.play()
        resetPlayer = False
        playBtn['image'] = pauseImg
        # call related functions
        getSongInfo()
        queue()
   
                            
def addSong():
    """Add selected song(s) to listbox"""
    global songDirDict
    # open window explorer and let user select song(s)
    filenames = filedialog.askopenfilenames()             
    for file in filenames:
        # add song at the end of the listbox
        lb.insert(END, os.path.basename(file))
        # add a new key(song name) and its value(song's directory) to songDirDict dictionary 
        songDirDict[os.path.basename(file)] = os.path.dirname(file)
        
    
def loopSong():
    """Repeat a song"""
    global songInLoop
    # Aactivate itself
    if songInLoop == False:
        songInLoop = True
        loopBtn['image'] = loopOnImg 
        checkSongStatus()
    # Deactivate itself
    elif songInLoop == True:
        songInLoop = False
        loopBtn['image'] = loopOffImg 

        
def checkSongStatus():
    "Check if beat player si playing song or is stopped"
    if songInLoop == True:
        # Refresh every second
        master.after(1000, checkSongStatus)
        # when song finishes playing, call playSong func and play the song again
        if mixer.music.get_busy() == 0 and resetPlayer == False:
            status.set("-")
            playSong()
        

def queue():
    """Play next song in queue"""
    global songDirDict
    # queue next song  if an active song isn't a last one and isStopped is false, otherwise by clicking on stop button it will play next song instead
    if mixer.music.get_busy() == 0:
        # without resetPlayer variable, beat player keeps playing next song in queue after click on stop button
        if (lb.index(playingSongIndex) < lb.size()-1) and (songInLoop == False) and (resetPlayer == False):
            # clear selected anchored song and select next one
            nextSongIndex=lb.index(playingSongIndex)+1
            lb.selection_clear(ANCHOR)
            lb.activate(nextSongIndex)
            status.set("-")
            playSong()
        # after last song in listbox, "deactivate" beat player
        elif lb.index(playingSongIndex) == lb.size()-1:
            stopSong()
    else:
        master.after(1000, queue)
    
        
def getSongInfo():
    """Get information about song"""
    global absolutPath, songLength, songInfo
    # get basic information about song...
    audio = MP3(absolutPath)
    # get song duration info
    songLength = int(audio.info.length)
    # get basic song info
    songInfo=mutagen.File(absolutPath, easy=True) 
    # ... and pass them on to related functions
    timeDisplay()
    songInfoDisplay(songInfo)
 
    
def click(event):
    """Play song on doubleclick event"""
    status.set("-")
    playBtn['image'] = playImg
    resetPlayer = False
    playSong()
    

def stopSong():
    """Stop playing song"""
    global  resetPlayer
    mixer.music.unpause()
    mixer.music.stop()
    # change value to variables and play button image
    status.set("-")
    resetPlayer = True
    playBtn['image'] = playImg
    
    
def nextSong():
    """Plays next song in the listbox"""
    if lb.index(playingSongIndex) < lb.size()-1:
        # clear selection of an anchored song and selects next one
        nextIndex=lb.index(playingSongIndex)+1
        lb.selection_clear(ANCHOR)
        lb.activate(nextIndex)
        status.set("-")
        playSong()


def prevSong():
    """Play previous song in the listbox"""
    if lb.index(playingSongIndex) > 0:
        # clear selection of an anchored song and selects previous one
        prevIndex=lb.index(playingSongIndex)-1
        lb.selection_clear(ANCHOR)
        lb.activate(prevIndex)
        status.set("-")
        playSong()


def songVolume(val):
    """Beat player volume"""
    volume = int(val)/100
    mixer.music.set_volume(volume)
    
    
def timeDisplay():
    """Display song length information and  passing time"""
    global time, songLength, status, mins, secs
    # start counting time since a song has been started
    if status.get() == ("-Playing"):
        master.after(1000, timeDisplay)
        mins, secs = divmod(mixer.music.get_pos()/1000, 60)
        time = secs + mins*60
    # reset time back to zero after song has finished
    elif status.get() == ("-"):
        mins = 0; secs = 0; time = 0
    # song length scale appears only during the time a song is playing
    songLengthScale.config(from_=0, to=songLength, orient=HORIZONTAL, sliderlength=10, showvalue=0, bd=0, length=300
                          , bg='#c0c5d2',fg="#c0c5d2", troughcolor='#da832f', highlightbackground="#c0c5d2")
    songLengthScale.grid(row=3, column=0)
    songLengthScale.set(time) 
    # update song counter
    counter.config(text="{:0>2}:{:0>2}".format(int(mins),int(secs)))
    

def songInfoDisplay(songInfo):
    """Display song information"""
    # Display song duration info
    mins, secs = divmod(songLength, 60)
    songDuration.config(text="{:0>2}:{:0>2}".format(int(mins),int(secs)))
    songDuration.grid(row=3, column=1, sticky = W)
    # Display song title and artist info
    titleLabel.config(text=songInfo["title"][0])
    artistLabel.config(text=songInfo["artist"][0])

    
"""BUTTON IMAGES"""
pauseImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\pause.png")
pauseImg = pauseImg.zoom(5) 
pauseImg = pauseImg.subsample(64) 

prevImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\prev.png")
prevImg = prevImg.zoom(5)
prevImg = prevImg.subsample(64)

playImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\play.png")
playImg = playImg.zoom(5) 
playImg = playImg.subsample(64) 

stopImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\stop.png")
stopImg = stopImg.zoom(5) 
stopImg = stopImg.subsample(64)

nextImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\next.png")
nextImg = nextImg.zoom(5)
nextImg = nextImg.subsample(64)

loopOffImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\loopOff.png")
loopOffImg = loopOffImg.zoom(5) 
loopOffImg = loopOffImg.subsample(64)

loopOnImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\loopOn.png")
loopOnImg = loopOnImg.zoom(5) 
loopOnImg = loopOnImg.subsample(64) 

addImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\add.png")
addImg = addImg.zoom(10)
addImg = addImg.subsample(64)

deleteImg = PhotoImage(file=r"C:\Users\Michal\Desktop\python\Images\delete.png")
deleteImg = deleteImg.zoom(10)
deleteImg = deleteImg.subsample(64)

"""SONG-INFO FRAME SETTINGS"""
songFrame = LabelFrame(master, text="Song Track", font=("calibri",11,"bold"), relief=GROOVE, bg='#383859', fg="#00ef00")
songFrame.place(x=2, y=0, width=420, height=120)

# Create Labels
counter=Label(songFrame, font=("calibri",11,"bold"), bg='#383859', fg="#00ef00")
songDuration=Label(songFrame, font=("calibri",11,"bold"), bg='#383859', fg="#00ef00")
titleLabel=Label(songFrame, font=("calibri",11,"bold"), bg='#383859', fg="#00ef00")
artistLabel=Label(songFrame, font=("calibri",11,"bold"), bg='#383859', fg="#00ef00")
songDuration=Label(songFrame, font=("calibri",11,"bold"), bg='#383859', fg="#00ef00")
songLengthScale = Scale(songFrame)

# Grid label settings
counter.grid(row=0, column=0, sticky = W)
titleLabel.grid(row=1, column=0, sticky = W)
artistLabel.grid(row=2, column=0, sticky = W)

"""CONTROL FRAME SETTINGS"""
controlFrame = LabelFrame(master,relief=GROOVE, bg='#383859')
controlFrame.place(x=2, y=120, width=420, height=45)

# Create Buttons
prevBtn = Button(controlFrame, image=prevImg, command=prevSong, bd=0, bg='#383859')
playBtn = Button(controlFrame, image=playImg, command=playSong, bd=0, bg='#383859')
stopBtn = Button(controlFrame, image=stopImg, command=stopSong, bd=0, bg='#383859')
nextBtn = Button(controlFrame, image=nextImg, command=nextSong, bd=0, bg='#383859')
loopBtn = Button(controlFrame, image=loopOffImg, command=loopSong, bd=0, bg='#383859')
volumeScale = Scale(controlFrame, from_=0, to=100, orient=HORIZONTAL, command=songVolume, sliderlength=15, 
                    bd=0, showvalue=0, length=200, bg='#c0c5d2',fg="#c0c5d2", troughcolor='#da832f', highlightbackground="#c0c5d2") #, activebackground="#da832f", highlightbackground="#da832f"
volumeScale.set(70)

# Grid buttons/scale settings
prevBtn.grid(row=0, column=0, sticky = W)
playBtn.grid(row=0, column=1, sticky = W)
stopBtn.grid(row=0, column=2, sticky = W)
nextBtn.grid(row=0, column=3, sticky=W)
loopBtn.grid(row=0, column=4, sticky=W)
volumeScale.grid(row=0, column=5, sticky=W)

"""PLAYLIST FRAME SETTINGS"""
playlistFrame = LabelFrame(master, text="Playlist", font=("calibri",11,"bold"), bg='#383859', fg="#00ef00", relief=GROOVE)
playlistFrame.place(x=422, y=0, width=420, height=165)

# Create playlist Listbox/scrollbar
lb = Listbox(playlistFrame, selectmode=EXTENDED, width=55, height=6, font=("calibri", 11, "bold"),
             bg='black', fg="#00ef00", bd=0, highlightthickness=0)

scrollbar = Scrollbar(playlistFrame, orient=VERTICAL)
scrollbar.config(command=lb.yview)
lb.config(yscrollcommand=scrollbar.set)

# Create playlist buttons
addBtn = Button(playlistFrame, image=addImg, command=addSong, bd=0,  bg='#383859')
delBtn = Button(playlistFrame, image=deleteImg, command=deleteSong, bd=0,  bg='#383859')

# Grid settings
lb.grid(row=0, column=0, columnspan=6)
scrollbar.grid(row=0, column=6,  sticky=NSEW)
addBtn.grid(row=1, column=0, sticky=W)
delBtn.grid(row=1, column=1, sticky=W)

"""BIND"""
lb.bind('<Double-1>', click)

mainloop()


# In[ ]:




