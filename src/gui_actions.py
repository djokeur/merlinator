# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.

import tkinter as tk

class GUIActions(tk.Tk):

    def on_closing(self):
        if tk.messagebox.askokcancel("Quitter", "Voulez vous quitter merlinator?"):
            if self.sessionfile and not self.sessionfile.closed:
                self.sessionfile.close()
            if self.enable_audio and self.audio_widget.sound:
                self.audio_widget.sound.close()
            self.quit()
            self.destroy()
            
    def setTitle(self, *args):
        title = self.title_entry.get()
        node = self.main_tree.selection()
        if self.main_tree.tag_has("directory", node):
            title = ' \u25AE ' + title
        else:
            title = ' \u266A ' + title
        self.main_tree.item(node, text=title)
        if self.fav_tree.exists(node):
            self.fav_tree.item(node, text=title)
            
            
            
    def sync_title_button(self, *args):
        current_string = self.title_entry.get()
        node = self.main_tree.selection()
        if current_string == self.main_tree.item(node, 'text')[3:]:
            self.buttonSetTitle['state'] = 'disabled'
        else:
            self.buttonSetTitle['state'] = 'normal'
            
            
            
    def sync_buttons_main(self, event=None):
        selected_node = self.main_tree.selection()
        if selected_node:
            self.title_entry['state'] = "normal"
            self.buttonSelectImage['state'] = 'normal'
            self.buttonDelete['state'] = 'normal'
            self.buttonToggleFavorite['state'] = 'normal'
            index = self.main_tree.index(selected_node)
            parent = self.main_tree.parent(selected_node)
            if index>0:
                self.buttonMoveUp['state'] = 'normal'
            else:
                self.buttonMoveUp['state'] = 'disabled'
            if index == len(self.main_tree.get_children(parent))-1:
                self.buttonMoveDown['state'] = 'disabled'
            else:
                self.buttonMoveDown['state'] = 'normal'
            if parent == '':
                self.buttonMoveParentDir['state'] = 'disabled'
            else:
                self.buttonMoveParentDir['state'] = 'normal'
            if self.enable_audio:
                self.audio_widget.init()
        else:
            self.title_entry['state'] = "disabled"
            self.buttonSelectImage['state'] = 'disabled'
            self.buttonDelete['state'] = 'disabled'
            self.buttonToggleFavorite['state'] = 'disabled'
            self.buttonMoveDown['state'] = 'disabled'
            self.buttonMoveUp['state'] = 'disabled'
            self.buttonMoveParentDir['state'] = 'disabled'
            if self.enable_audio:
                self.audio_widget.init()
            
            
    
    def sync_buttons_fav(self, event=None):
        selected_node = self.fav_tree.selection()
        if selected_node:
            index = self.fav_tree.index(selected_node)
            if index>0:
                self.buttonMoveUpFav['state'] = 'normal'
            else:
                self.buttonMoveUpFav['state'] = 'disabled'
            if index == len(self.fav_tree.get_children(self.fav_tree.parent(selected_node)))-1:
                self.buttonMoveDownFav['state'] = 'disabled'
            else:
                self.buttonMoveDownFav['state'] = 'normal'
        else:
            self.buttonMoveDownFav['state'] = 'disabled'
            self.buttonMoveUpFav['state'] = 'disabled'
        

    def synchronise_selection(self, event):
        w = event.widget
        if w == self.main_tree:
            selected_node = w.selection()
            if selected_node and self.fav_tree.exists(selected_node):
                if self.fav_tree.selection() != selected_node:
                    self.fav_tree.selection_set(selected_node)
                    self.fav_tree.see(selected_node)
            else:
                if self.fav_tree.selection():
                    self.fav_tree.selection_set([])
            self.title_entry.delete(0, 'end')
            self.title_entry.insert(0, self.main_tree.item(self.main_tree.selection(),'text')[3:])
            self.sync_buttons_main()
            
        elif w == self.fav_tree:
            selected_node = w.selection()
            if selected_node and self.main_tree.selection() != selected_node:
                    self.main_tree.selection_set(selected_node)
                    self.main_tree.see(selected_node)
            self.sync_buttons_fav()
        else:
            return
        

class TwoButtonCancelDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title, prompt, button0text, button1text):
        self.res = 2
        self.prompt = prompt
        self.button0text = button0text
        self.button1text = button1text
        super().__init__(parent, title)
        
    def body(self, frame):
        # print(type(frame)) # tkinter.Frame
        self.label = tk.Label(frame, width=40, text=self.prompt)
        self.label.pack()
        return frame
        
    def button_pressed(self, button):
        self.res = button
        self.destroy()


    def buttonbox(self):
        self.button0 = tk.Button(self, text=self.button0text, width=12, command=lambda:self.button_pressed(0))
        self.button0.focus_set()
        self.button0.focus()
        self.button0.pack(fill=tk.NONE, expand=True, side=tk.LEFT)
        self.button1 = tk.Button(self, text=self.button1text, width=12, command=lambda:self.button_pressed(1))
        self.button1.pack(fill=tk.NONE, expand=True, side=tk.LEFT)
        self.cancel_button = tk.Button(self, text='Annuler', width=12, command=lambda:self.button_pressed(2))
        self.cancel_button.pack(fill= tk.NONE, expand=True, side=tk.RIGHT)
        self.bind("<Escape>", lambda event: self.button_pressed(2))
        self.bind("<Return>", lambda event: self.focus_get().invoke() if hasattr(self.focus_get(), 'invoke') else None)
        
       
