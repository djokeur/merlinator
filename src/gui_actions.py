# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.

import tkinter as tk

class GUIActions(tk.Tk):

    def on_closing(self):
        if True or tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.sessionfile and not self.sessionfile.closed:
                self.sessionfile.close()
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
        else:
            self.title_entry['state'] = "disabled"
            self.buttonSelectImage['state'] = 'disabled'
            self.buttonDelete['state'] = 'disabled'
            self.buttonToggleFavorite['state'] = 'disabled'
            self.buttonMoveDown['state'] = 'disabled'
            self.buttonMoveUp['state'] = 'disabled'
            self.buttonMoveParentDir['state'] = 'disabled'
            
    
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
        