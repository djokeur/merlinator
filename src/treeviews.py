# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.


import tkinter as tk
from tkinter.ttk import Treeview
from PIL import Image, ImageTk
import os.path, shutil, uuid
from time import time

from io_utils import *



class MerlinTree(Treeview):

    def __init__(self, parent, root=None):
        Treeview.__init__(self, parent, selectmode='browse', show='tree')
        if root is None:
            self.rootGUI = parent
        else:
            self.rootGUI = root

        self.bind('<B1-Motion>', self.rootGUI.movemouse)
        self.bind("<ButtonRelease-1>", self.rootGUI.mouserelease)
        
        self.bind("<Control-Up>", self.moveUp)
        self.bind("<Control-Down>", self.moveDown)
        self.bind("<Control-Left>", self.moveParentDir)
        self.bind("<KeyPress-Control_L>", self.disable_arrows)
        self.bind("<KeyRelease-Control_L>", self.enable_arrows)
        self.bind("<KeyPress-Control_R>", self.disable_arrows)
        self.bind("<KeyRelease-Control_R>", self.enable_arrows)
        
        self.bind('<<TreeviewSelect>>', self.rootGUI.synchronise_selection)

    def disable_arrows(self, *args):
        temp = self.bind_class('Treeview', '<Up>')
        if temp: 
            self.boundUp = self.bind_class('Treeview', '<Up>')
        temp = self.bind_class('Treeview', '<Down>')
        if temp:
            self.boundDown = temp
        temp = self.bind_class('Treeview', '<Left>')
        if temp:
            self.boundLeft = temp
        self.unbind_class('Treeview', '<Up>')
        self.unbind_class('Treeview', '<Down>')
        self.unbind_class('Treeview', '<Left>')
        
    def enable_arrows(self, *args):
        self.bind_class('Treeview', '<Up>', self.boundUp)
        self.bind_class('Treeview', '<Down>', self.boundDown)
        self.bind_class('Treeview', '<Left>', self.boundLeft)
        
        
    def moveUp(self, *args):
        node = self.selection()
        if node:
            self.move(node, self.parent(node), self.index(node)-1)
            self.see(node)
            
    def moveDown(self, *args):
        node = self.selection()
        if node:
            self.move(node, self.parent(node), self.index(node)+1)
            self.see(node)
            
    def moveParentDir(self, *args):
        node = self.selection()
        if node and self.parent(node) != '':
            self.move(node, self.parent(self.parent(node)), 'end')
            self.see(node)

    def get_ancestors(self, node):
        res = [node]
        parent = self.parent(node)
        while parent:
            res.append(parent)
            parent = self.parent(parent)
        return res
 

class MerlinMainTree(MerlinTree):


    COL = ("Favori", "imagepath", "soundpath", "id", "parent_id", "order", "nb_children", 
           "fav_order", "type", "limit_time", "add_time", 
           "uuid", "title")

    rootItem = {'id': 1, 'parent_id': 0, 'order': 0, 'nb_children': 0, 
                'fav_order': 0, 'type': 1, 'limit_time': 0, 'add_time': 0, 
                'uuid': '', 'title': 'Root', 'imagepath': '', 'soundpath': ''}
    favItem = {'id': 2, 'parent_id': 1, 'order': 0, 'nb_children': 0,
               'fav_order': 0, 'type': 10, 'limit_time': 0, 'add_time': 0, 
               'uuid': 'cd6949db-7c5f-486a-aa2b-48a80a7950d5', 'title': 'Merlin_favorite', 
               'imagepath': '../res/defaultPics.zip', 'soundpath': ''}
    recentItem = {'id': 3, 'parent_id': 1, 'order': 1, 'nb_children': 0, 
                  'fav_order': 0, 'type': 18, 'limit_time': 0, 'add_time': 0, 
                  'uuid': '8794f486-c461-4ace-a44b-85c359f84017', 'title': 'Merlin_discover', 
                  'imagepath': '../res/defaultPics.zip', 'soundpath': ''}
    defaultItems = [rootItem, favItem, recentItem]
    
    def __init__(self, parent, root=None):
        MerlinTree.__init__(self, parent, root)
        
        self.currently_selected = []
        self.iid_Merlin_favorite = None
        self.iid_Merlin_discover = None


        self["columns"] = MerlinMainTree.COL
        self.column("#0", width=300)
        self.column("Favori", width=20, minwidth=10, stretch=tk.NO)
        # self.column("id", width=20, minwidth=10, stretch=tk.NO)
        # self.column("parent_id", width=20, minwidth=10, stretch=tk.NO)
        # self.column("order", width=20, minwidth=10, stretch=tk.NO)
        # self.column("nb_children", width=20, minwidth=10, stretch=tk.NO)
        # self.column("fav_order", width=20, minwidth=10, stretch=tk.NO)
        # self.column("type", width=20, minwidth=10, stretch=tk.NO)
        # self.column("limit_time", width=20, minwidth=10)
        # self.column("add_time", width=20, minwidth=10)
        # self.column("uuid", width=100, minwidth=50)
        # self.column("title", width=100, minwidth=50)
        self["displaycolumns"]=["Favori"]
        
        # self.heading('#0',text='Nom', anchor=tk.W)
        # for key in MerlinMainTree.COL:
            # self.heading(key, text=key, anchor=tk.W)
        
        self.tag_configure("directory", foreground="grey")
        

    
        
    
    def populate(self, items, thumbnails):
        # clear existing data
        for c in self.get_children():
            self.delete(c)
        if self.iid_Merlin_discover:
            self.delete(self.iid_Merlin_discover)
        if self.iid_Merlin_favorite:
            self.delete(self.iid_Merlin_favorite)
        
        # adding data
        for item in items:
            favorite = '♥' if item['fav_order'] else ''
            data = tuple([ favorite] + \
                [item[key] for key in MerlinMainTree.COL[1:]])
            iid = item['id']
            if item['parent_id']==1:
                parent = ''
            else:
                parent = item['parent_id']
            if item['type']==1: # root
                continue
            self.insert(parent, item['order'], iid=iid, text=item['title'], values=data, image=thumbnails[item['uuid']])
            if item['type'] in [2, 34]: # directory 
                self.item(iid, tags="directory")
                self.item(iid, text=' \u25AE ' + self.item(iid, 'text'))
            elif item['type']==10: # favoris
                self.item(iid, tags="directory")
                self.item(iid, text=' \u25AE ' + self.item(iid, 'text'))
                self.iid_Merlin_favorite = iid
                self.detach(iid)
            elif item['type']==18: # ajouts récents
                self.item(iid, tags="directory")
                self.item(iid, text=' \u25AE ' + self.item(iid, 'text'))
                self.iid_Merlin_discover = iid
                self.detach(iid)
            else:
                self.item(iid, text=' \u266A ' + self.item(iid, 'text'))
                if item['fav_order']>0:
                    self.item(iid, tags=("sound", "favorite"))
                else:
                    self.item(iid, tags="sound")
                
        self.update()
                
        
    def make_item_list(self):
        
        root_item = MerlinMainTree.rootItem
        children = self.get_children('')
        root_item['nb_children'] = len(children)
        items = [root_item]
        self.nb_fav = len(self.tag_has("favorite"))
        counter = 1
        for order, c in enumerate(children):
            sublist, counter = self.subtree_to_list(c, counter, order)
            items.extend(sublist)
        order = len(children)
        if self.iid_Merlin_favorite:
            item = format_item(self.set(self.iid_Merlin_favorite))
            counter += 1
            item['id'] = counter
            item['order'] = order
            order += 1
            item['parent_id'] = root_item['id']
            root_item['nb_children'] += 1
            item['nb_children'] = self.nb_fav
            items.append(item)
        if self.iid_Merlin_discover:
            item = format_item(self.set(self.iid_Merlin_discover))
            counter += 1
            item['id'] = counter
            item['order'] = order
            order += 1
            item['parent_id'] = root_item['id']
            root_item['nb_children'] += 1
            items.append(item)
        
        return items
        
        
    def subtree_to_list(self, node, counter=0, order=0, parent=1):
        item = format_item(self.set(node))
        children = self.get_children(node)
        counter += 1
        item['id'] = counter
        item['order'] = order
        item['parent_id'] = parent
        item['nb_children'] = len(children)
        item['title'] = self.item(node, "text")[3:]
        if self.tag_has('favorite', node):
            item['fav_order'] = self.nb_fav - self.rootGUI.fav_tree.index(node)
        items = [item]
        for order, c in enumerate(children):
            sublist, counter = self.subtree_to_list(c, counter, order, item['id'])
            items.extend(sublist)
        return items, counter
           
    def set_selection(self, *args):
        self.current_selection = self.selection()
      
    
    def reset_selection(self, *args):
        self.selection_set(self.current_selection)
        self.focus(self.current_selection)

    def deleteNode(self, *args):
        node = self.selection()
        if self.rootGUI.focus_get() in [self.rootGUI, self]:
            if not node:
                return
            if self.tag_has('directory', node):
                node_type = 'menu'  
            else:
                node_type = 'fichier'
            detail = ''
            if node_type == 'menu' and self.get_children(node):
                detail = " et tout ce qu'il contient"
            question = f"Effacer le {node_type} '{self.item(node, 'text')[3:]}'{detail} ?"
            answer = tk.messagebox.askyesno("Confirmation",question)
            if answer:
                self.delete(node)
                fav_tree = self.rootGUI.fav_tree
                if fav_tree.exists(node):
                    fav_tree.delete(node)

    def add_menu(self):
        current_node = self.selection()
        iid = self.insert(self.parent(current_node), self.index(current_node)+1, text=' \u25AE Nouveau Menu', tags="directory")
        self.set(iid, 'type', '2')
        self.set(iid, 'add_time', str(int(time())))
        self.set(iid, 'title', 'Nouveau Menu')
        self.set(iid, 'uuid', str(uuid.uuid4()))
        self.focus(iid)
        self.selection_set(iid)
        self.update()
        self.rootGUI.title_entry.focus_set()

    def add_sound(self):
        current_node = self.selection()
        playlist_dirname = os.path.dirname(self.rootGUI.playlistpath)
        filepaths = filedialog.askopenfilename(initialdir=playlist_dirname, filetypes=[('mp3', '*.mp3')], multiple=True)
        if not filepaths:
            return
        for filepath in filepaths:
            dirname, basename = os.path.split(filepath)
            # if dirname != playlist_dirname:
                # answer = tk.messagebox.askyesnocancel("Copier Fichier?", "Copier le fichier dans le dossier de la playlist ?")
                # if answer is None:
                    # return
                # elif answer:
                    # new_filepath = playlist_dirname + basename
                    # if os.path.exists(new_filepath):
                        # answer = tk.messagebox.askokcancel("Fichier existant", "Le fichier existe déjà. L'écraser ?")
                        # if not answer:
                            # return
                    # shutil.copyfile(filepath, new_filepath)
                    # filepath = new_filepath
                    # dirname, basename = os.path.split(filepath)        
            uuid, ext = os.path.splitext(basename)
            iid = self.insert(self.parent(current_node), self.index(current_node)+1, text=' \u266A ' + uuid, tags='sound')
            self.set(iid, 'type', '4')
            self.set(iid, 'soundpath', filepath)
            self.set(iid, 'add_time', str(int(time())))
            self.set(current_node, 'uuid', uuid)
        if len(filepaths)==1:
            self.focus(iid)
            self.selection_set(iid)
        self.update()

    def select_image(self):
        current_node = self.selection()
        playlist_dirname = os.path.dirname(self.rootGUI.playlistpath)
        if not current_node:
            return
        uuid = self.set(current_node, 'uuid')
        if uuid:
            initfile = uuid+'.jpg'
        else:
            initfile = ''
        filepath = filedialog.askopenfilename(initialdir=playlist_dirname, initialfile=initfile, filetypes=[('images jpg', '*.jpg')])
        if not filepath:
            return
        dirname, basename = os.path.split(filepath)
        
        # if self.tag_has('directory', current_node):
            # if dirname != playlist_dirname:
                # answer = tk.messagebox.askyesnocancel("Copier Fichier?", "Copier le fichier dans le dossier de la playlist ?")
                # if answer is None:
                    # return
                # elif answer:
                    # new_filepath = os.path.join(playlist_dirname, basename)
                    # if os.path.exists(new_filepath):
                        # answer = tk.messagebox.askokcancel("Fichier existant", f"Le fichier {new_filepath} existe déjà. L'écraser ?")
                        # if not answer:
                            # return
                    # with Image.open(filepath) as image:
                        # image_thumbnail = image.resize((128,128), Image.ANTIALIAS)
                        # image_thumbnail.save(new_filepath, "JPEG", mode='RGB')
                    # filepath = new_filepath
                    # dirname, basename = os.path.split(filepath)
            # uuid, ext = os.path.splitext(basename)
            # self.set(current_node, 'uuid', uuid)
        # else:
            # uuid = self.set(current_node, 'uuid')
            # new_filepath = os.path.join(playlist_dirname, uuid + '.jpg')
            # mismatch = False
            # if dirname != playlist_dirname:
                # mismatch = True
                # answer = tk.messagebox.askyesnocancel("Copier Fichier?", "Copier le fichier image dans le dossier de la playlist ?")
            # elif filepath != new_filepath:
                # mismatch = True
                # answer = tk.messagebox.askyesnocancel("Copier Fichier?", "Copier et renomer le fichier image ?")
            # if mismatch:
                # if answer is None:
                    # return
                # elif answer:
                    # if os.path.exists(new_filepath):
                        # answer = tk.messagebox.askokcancel("Fichier existant", "Le fichier existe déjà. L'écraser ?")
                        # if not answer:
                            # return
                    # with Image.open(filepath) as image:
                        # image_thumbnail = image.resize((128,128), Image.ANTIALIAS)
                        # image_thumbnail.save(new_filepath, "JPEG", mode='RGB')
                    # filepath = new_filepath
                    # dirname, basename = os.path.split(filepath)
                
        if uuid not in self.rootGUI.thumbnails:
            with Image.open(filepath) as image:
                image_small = image.resize((40, 40), Image.ANTIALIAS)
                self.rootGUI.thumbnails[uuid] = ImageTk.PhotoImage(image_small)
        
        self.item(current_node, image=self.rootGUI.thumbnails[uuid])
        self.set(current_node, 'imagepath', filepath)
        self.update()
        
    
    
    def toggleFavorite(self, *args):
        node = self.selection()
        if self.tag_has('favorite', node):
            self.removeFromFavorite(node)
        else:
            self.addToFavorite(node)
        
    def addToFavorite(self, node, index='end'):
        if node and self.tag_has('sound', node) and not self.tag_has('favorite', node):
            self.item(node, tags=('sound', 'favorite'))
            self.set(node, 'Favori', '♥')
            self.rootGUI.fav_tree.insert('', 'end', iid=node, \
                                         text=self.item(node, 'text'), \
                                         image=self.item(node, 'image'))
            self.rootGUI.fav_tree.selection_set(node)
            self.rootGUI.fav_tree.see(node)
            self.update()
            self.rootGUI.fav_tree.update()
        
    def removeFromFavorite(self, node):
        node = self.selection()
        if node and self.tag_has('sound', node):
            self.item(node, tags=('sound'))
            self.set(node, 'Favori', '')
            self.rootGUI.fav_tree.delete(node)
            self.update()
            self.rootGUI.fav_tree.update()
            

    

class MerlinFavTree(MerlinTree):
    
    def __init__(self, parent, root=None):
        MerlinTree.__init__(self, parent, root)
        
    
    def populate(self, main_tree):
        # clear existing data
        for c in self.get_children():
            self.delete(c)
        
        # add data
        fav_list = sorted([(int(main_tree.set(node,'fav_order')), node) for node in main_tree.tag_has('favorite')], reverse=True)
        for order, fav in enumerate(fav_list):
            node = fav[1]
            self.insert('', order, iid=node, text=main_tree.item(node, 'text'), \
                        image=main_tree.item(node, 'image'))
        self.update()
    
    