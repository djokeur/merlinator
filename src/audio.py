# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.


#importing libraries 
from pygame import mixer
import time
import tkinter as tk
from tkinter import ttk
import zipfile
from mutagen.mp3 import MP3

class AudioWidget(tk.Frame):
    
    
    def __init__(self, parent, root=None, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        if root is None:
            self.rootGUI = parent
        else:
            self.rootGUI = root
        mixer.init()
        self.sound = None
        self.start_time = 0
        self.pause_time = 0
        self.sound_length = 0
        self.looping = False
        self.playing = False
    
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        #slider
        self.slider = ttk.Scale(self, orient='horizontal', from_=0, value=0, to=0, command = self.slider_action)
        self.slider.grid(row=0, column=0, columnspan=3, sticky='ew')
        #slider label
        self.slider_label = tk.Label(self, text="00:00 / 00:00")
        self.slider_label.grid(row=1, column=2, sticky="e")
        #play/pause button
        self.play_button=tk.Button(self,text="Play/Pause",width =8,command=self.PlayPause, state='disabled')
        self.play_button.grid(row=1,column=0)
        #stop button
        self.stop_button=tk.Button(self,text="Stop",width =8,command=self.Stop, state='disabled')
        self.stop_button.grid(row=1,column=1)
        
        self.slider.bind('<Button-1>', self.conditionalPause)
        self.slider.bind("<ButtonRelease-1>", self.conditionalResume)
    
    def slider_action(self, pos):
        position = self.slider.get()
        if self.start_time:
            elapsed_time = time.strftime("%M:%S", time.gmtime(position))
            total_time = time.strftime("%M:%S", time.gmtime(self.sound_length))
            self.slider_label.config(text=f"{elapsed_time} / {total_time}")
            if self.pause_time:
                self.start_time = self.pause_time - position
            else:
                self.start_time = time.time() - position
                mixer.music.play(start=position)
            
        
    def update_play_time(self):
        total_time = time.strftime("%M:%S", time.gmtime(self.sound_length))
        if self.start_time:
            if self.pause_time:
                current_time = self.pause_time - self.start_time
            else:
                current_time = time.time() - self.start_time
        else:
            current_time = 0
        elapsed_time = time.strftime("%M:%S", time.gmtime(current_time))
        self.slider_label.config(text=f"{elapsed_time} / {total_time}")
        self.slider.config(value=current_time)
        self.after(200, self.update_play_time)
            
    
    def init(self):
        main_tree = self.rootGUI.main_tree
        selected_node = main_tree.selection()
        self.Stop()
        if self.sound:
            self.sound.close()
        self.start_time = 0
        self.pause_time = 0
        self.sound = None
        self.sound_length = 0
            
        if selected_node and main_tree.tag_has('sound', selected_node) and main_tree.set(selected_node, 'soundpath'):
            soundpath = main_tree.set(selected_node, 'soundpath')
            if soundpath[-4:] == '.zip':
                filename = main_tree.set(selected_node, 'uuid') + '.mp3'
                with zipfile.ZipFile(soundpath, 'r') as z:
                    zippath = zipfile.Path(z, at=filename)
                    if zippath.exists():
                        self.sound = z.open(filename, 'r')
                        sound_mut = MP3(self.sound)
                        self.sound_length = sound_mut.info.length
                        self.sound.close()
                        self.sound = z.open(filename, 'r')
            else:
                self.sound = open(soundpath, 'rb')
                sound_mut = MP3(self.sound)
                self.sound_length = sound_mut.info.length
                self.sound.close()
                self.sound = open(soundpath, 'r')
            
            self.slider.config(to=self.sound_length)
            self.play_button['state'] = 'normal'
        else:
            self.play_button['state'] = 'disabled'
            self.config(to=0)
                
        self.stop_button['state'] = 'disabled'
        if not self.looping:
                self.update_play_time()
                self.looping = True
            
            
    
    def Play(self):
        if self.sound:
            mixer.music.load(self.sound)
            self.pause_time = 0
            self.start_time = time.time()
            mixer.music.play()
            self.stop_button['state'] = 'normal'
            
    def Pause(self):
        self.pause_time = time.time()
        mixer.music.pause()
    
    def Stop(self):
        mixer.music.stop()
        if self.start_time:
            self.start_time = 0
            self.pause_time = 0
            self.stop_button['state'] = 'disabled'
        
    def Resume(self):
        delta = time.time() - self.pause_time
        self.pause_time = 0
        self.start_time += delta
        mixer.music.unpause()
        
            
    def PlayStop(self, event=None):
        if self.sound:
            self.Stop()
        else:
            self.Play()
    
    
    def PlayPause(self, event=None):
        if self.start_time:
            if self.pause_time:
                self.Resume()
            else:
                self.Pause()
        else:
            self.Play()
            
    def conditionalPause(self, event=None):
        if self.start_time and not self.pause_time:
            self.playing = True
            self.Pause()
            
    def conditionalResume(self, event=None):
        if self.playing:
            self.Resume()
            self.playing = False
        self.slider_action(None)
            
    
            