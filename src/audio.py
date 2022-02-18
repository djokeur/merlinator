# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.


#importing libraries 
from pygame import mixer
import tkinter as tk
import zipfile

class AudioWidget(tk.Frame):
    
    
    def __init__(self, parent, root=None, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        if root is None:
            self.rootGUI = parent
        else:
            self.rootGUI = root    
        self.sound = ''
        mixer.init()
            
            
    
    def Play(self):
        main_tree = self.rootGUI.main_tree
        selected_node = main_tree.selection()
        if main_tree.tag_has('sound') and main_tree.set(selected_node, 'soundpath'):
            soundpath = main_tree.set(selected_node, 'soundpath')
            if soundpath[-4:] == '.zip':
                filename = main_tree.set(selected_node, 'uuid') + '.mp3'
                with zipfile.ZipFile(soundpath, 'r') as z:
                    zippath = zipfile.Path(z, at=filename)
                    if zippath.exists():
                        self.sound = z.open(filename, 'r')
            else:
                self.sound = open(soundpath, 'r')
            mixer.music.load(self.sound)
            mixer.music.play()
            
    def Pause(self):
        mixer.music.pause()
    
    def Stop(self):
        mixer.music.stop()
        self.sound.close()
        self.sound = ''
        
    def Resume(self):
        mixer.music.unpause()
            
    def PlayStop(self, event=None):
        if self.sound:
            self.Stop()
        else:
            self.Play()
            
            
            
    
            