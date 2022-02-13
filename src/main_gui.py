# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.


import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
from PIL.ImageTk import PhotoImage
import os.path, zipfile

from io_utils import *
from treeviews import *


class MerlinGUI(tk.Tk):
    
    def __init__(self):
        # create root window
        tk.Tk.__init__(self)
        self.title('Merlinator')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.sessionpath = ''
        self.sessionfile = None
        self.thumbnails = {}
        self.moveitem = tk.StringVar()
        self.src_widget = None
        self.save_cursor = self['cursor'] or ''

        
        # configure the grid layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.maxsize(width=screen_w, height=screen_h)
        # rw = int(screen_w / 2)
        # rh = int(screen_h / 2)
        # self.geometry('{}x{}+{:g}+{:g}'.format(rw, rh, rw / 2, rh / 2))
        self.geometry('{}x{}+{:g}+{:g}'.format(670, 500, 300, 200))
        self.update()
        
        # Create menu
        top_menu = tk.Menu(self)
        self.config(menu=top_menu)
        file_menu = tk.Menu(top_menu, tearoff=False)
        top_menu.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label="Nouvelle session", command=self.new_session)
        file_menu.add_command(label="Ouvrir session", command=self.load_session)
        file_menu.add_command(label="Sauver session", command=self.save_session)
        file_menu.add_command(label="Sauver session sous", command=self.saveas_session)
        file_menu.add_command(label="Importer playlist", command=self.import_playlist)
        file_menu.add_command(label="Exporter playlist", command=self.export_playlist)
        file_menu.add_command(label="Importer archive", command=self.import_playlist_from_zip)
        file_menu.add_command(label="Exporter archive", command=self.export_all_to_zip)
        file_menu.add_command(label="Quitter", command=self.quit)

        self.grid_columnconfigure(0, weight=1)
        
        # Main paned window
        self.main_paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned_window.grid(row=0, column=0, sticky='eswn')
        
        # Main tree area
        self.main_tree_area = tk.LabelFrame(self.main_paned_window, text="Playlist", width=400)
        self.main_tree_area.grid_rowconfigure(0, weight=1)
        self.main_tree_area.grid_columnconfigure(0, weight=1)
        self.main_tree_area.grid_propagate(0)
        self.main_paned_window.add(self.main_tree_area)
        
        style = ttk.Style()
        style.configure("Treeview", rowheight=40)        
        self.update()
        
        self.make_main_tree(self.main_tree_area)
        
        # Control Frame
        self.control_frame = tk.Frame(self.main_paned_window, width=260)
        self.control_frame.grid_rowconfigure(3, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)
        self.control_frame.grid_propagate(0)
        self.main_paned_window.add(self.control_frame, sticky="nsew")
        
        # Title 
        self.title_label_frame = tk.LabelFrame(self.control_frame, text="Titre du son/menu", height=2, padx=5)
        self.title_label_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        self.title_label_frame.grid_columnconfigure(0, weight=1)
        self.title_entry = tk.Entry(self.title_label_frame)
        self.title_entry.grid(row=0, column=0, sticky='ew')
        self.title_entry.bind('<Return>', self.setTitle)
        self.buttonSetTitle = tk.Button(self.title_label_frame, text="Mettre à jour le titre",fg="black", command=self.setTitle)
        self.buttonSetTitle.grid(row=1, column=0)
        
        
        # Edition Area
        self.edition_area = tk.LabelFrame(self.control_frame, text='Édition')
        self.edition_area.grid(row=1, column=1, sticky='en')
        
        self.buttonDelete = tk.Button(self.edition_area, text="Supprimer", command=self.main_tree.deleteNode)
        self.buttonSelectImage = tk.Button(self.edition_area, text="Changer image", command=self.main_tree.select_image)
        self.buttonAddMenu = tk.Button(self.edition_area, text="Nouveau Menu", command=self.main_tree.add_menu)
        self.buttonAddSound = tk.Button(self.edition_area, text="Nouveau Son", command=self.main_tree.add_sound)
                
        # self.edition_area.grid_rowconfigure(0, weight=1)
        # self.edition_area.grid_rowconfigure(1, weight=1)
        # self.edition_area.grid_rowconfigure(2, weight=1)
        # self.edition_area.grid_rowconfigure(3, weight=1)
        
        self.buttonSelectImage.grid(row=0, column=0, sticky='ew')
        self.buttonDelete.grid(row=1, column=0, sticky='ew')
        self.buttonAddMenu.grid(row=2, column=0, sticky='ew')
        self.buttonAddSound.grid(row=3, column=0, sticky='ew')
        
        
        # Displacement Buttons
        self.main_tree_button_area = tk.LabelFrame(self.control_frame, text='Déplacer\nélément', width=60)
        self.main_tree_button_area.grid(row=1, column=0, sticky='nw')
        
        buttonMoveUp = tk.Button(self.main_tree_button_area, text="\u21D1",fg="black", width=5, command=self.main_tree.moveUp)
        buttonMoveUp.grid(row=0, column=0)
        buttonMoveParentDir = tk.Button(self.main_tree_button_area, text="\u21D0",fg="black", width=5, command=self.main_tree.moveParentDir)
        buttonMoveParentDir.grid(row=1, column=0)
        buttonMoveDown = tk.Button(self.main_tree_button_area, text="\u21D3",fg="black", width=5, command=self.main_tree.moveDown)
        buttonMoveDown.grid(row=2, column=0)
         
         
        
        # Favorite tree area
        self.fav_tree_area = tk.LabelFrame(self.control_frame, text="Favoris", width=200)
        self.fav_tree_area.grid_rowconfigure(0, weight=1)
        self.fav_tree_area.grid_columnconfigure(0, weight=1)
        self.fav_tree_area.grid(row=3, column=0, columnspan=2, sticky='nsew')
        self.fav_tree_area.grid_propagate(0)
        self.make_fav_tree(self.fav_tree_area)
        
        
        #Favorite Button
        self.buttonToggleFavorite = tk.Button(self.control_frame, text="Ajouter/retirer\ndes favoris", command=self.main_tree.toggleFavorite)
        self.buttonToggleFavorite.grid(row=2, column=0, sticky='sw')
        
        self.fav_tree_button_area = tk.LabelFrame(self.control_frame, text='Déplacer favori')
        self.fav_tree_button_area.grid(row=2, column=1, sticky='sw')
        buttonMoveUpFav = tk.Button(self.fav_tree_button_area, text="\u21D1",fg="black", width=5, command=self.fav_tree.moveUp)
        buttonMoveUpFav.grid(row=0, column=0)
        buttonMoveDownFav = tk.Button(self.fav_tree_button_area, text="\u21D3",fg="black", width=5, command=self.fav_tree.moveDown)
        buttonMoveDownFav.grid(row=0, column=1)
        
        self.update()
        
        
        self.bind("<BackSpace>", self.main_tree.deleteNode)
        self.bind("<Delete>", self.main_tree.deleteNode)
        

    def on_closing(self):
        if True or tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.sessionfile and not self.sessionfile.closed:
                self.sessionfile.close()
            self.quit()
            self.destroy()


    def populate_trees(self, items):
        self.main_tree.populate(items, self.thumbnails)
        self.fav_tree.populate(self.main_tree)


    def load_thumbnails(self, items):
        self.thumbnails = {}
        for item in items:
            imagepath = item['imagepath']
            if os.path.exists(imagepath):
                with Image.open(imagepath) as image:
                    image_small = image.resize((40, 40), Image.ANTIALIAS)
                    self.thumbnails[item['uuid']] = PhotoImage(image_small)
            else:
                self.thumbnails[item['uuid']] = ''
                
    
    def load_thumbnails_from_zip(self, items, zfile):
        self.thumbnails = {}
        for item in items:
            if item['uuid'] in self.thumbnails:
                continue
            filename = item['uuid'] + '.jpg'
            zippath = zipfile.Path(zfile, at=filename)
            if zippath.exists():
                with zfile.open(filename, 'r', pwd=info) as imagefile:
                    with Image.open(imagefile) as image:
                        image_small = image.resize((40, 40), Image.ANTIALIAS)
                        self.thumbnails[item['uuid']] = PhotoImage(image_small)
            else:
                self.thumbnails[item['uuid']] = ''    
                
    

    def import_playlist(self):
        self.playlistpath = filedialog.askopenfilename(initialfile="playlist.bin", filetypes=[('binary', '*.bin')])
        dirname = os.path.dirname(self.playlistpath)
        try: 
            with open(self.playlistpath, "rb") as file:
                items = read_merlin_playlist(file)
                for item in items:
                    if item['type'] == 1: # root
                        item['imagepath'] = ''
                    else:
                        item['imagepath'] = os.path.join(dirname, item['uuid'] + '.jpg')
                    if item['type'] in [4, 36]:
                        soundpath = os.path.join(dirname, item['uuid'] + '.mp3')
                        item['soundpath'] = soundpath
                    else:
                        item['soundpath'] = ''
            self.load_thumbnails(items)
            self.populate_trees(items)
        except IOError:
            tk.messagebox.showwarning("Erreur", "Fichier non accessible")
            
            
    def import_playlist_from_zip(self):
        filepath = filedialog.askopenfilename(initialfile="merlin.zip", filetypes=[('fichier zip', '*.zip')])
        if not filepath:
            return
        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                with z.open("playlist.bin", "r") as file:
                    items = read_merlin_playlist(file)
                for item in items:
                    item['imagepath'] = filepath
                    if item['type'] in [4, 36]:
                        item['soundpath'] = filepath
                    else:
                        item['soundpath'] = ''
                self.load_thumbnails_from_zip(items, z)
                self.populate_trees(items)
        except IOError:
            tk.messagebox.showwarning("Erreur", "Fichier non accessible")


    def export_playlist(self):
        t = self.main_tree
        if not t.get_children(''):
            return
        filepath = filedialog.asksaveasfilename(initialfile="playlist.bin", filetypes=[('binaire', '*.bin')])
        try:
            with open(filepath, "wb") as file:
                items = t.make_item_list()
                write_merlin_playlist(file, items)
        except IOError:
            tk.messagebox.showwarning("Erreur", "Fichier non accessible")     
   

    def export_all_to_zip(self):
        t = self.main_tree
        if not t.get_children(''):
            return
        filepath = filedialog.asksaveasfilename(initialfile="merlin.zip", filetypes=[('archive zip', '*.zip')])
        try:
            with zipfile.ZipFile(filepath, 'w') as zfile:
                items = self.main_tree.make_item_list()
                files_not_found = export_merlin_to_zip(items, zfile)
            if files_not_found:
                message = "Les fichiers suivants n'ont pas été trouvés:\n" + "\n".join([f"- '{f}'" for f in files_not_found])
                tk.messagebox.showwarning("Fichiers non trouvés", message)
        except IOError:
            tk.messagebox.showwarning("Erreur", "Fichier non accessible")
        
    def new_session(self):
        items = MerlinMainTree.defaultItems
        with zipfile.ZipFile('../res/defaultPics.zip', 'r') as zfile:
            self.load_thumbnails_from_zip(items, zfile)
        self.populate_trees(items)
        
    def save_session(self):
        if not self.sessionfile:
            self.saveas_session()
            return
        elif not self.main_tree.get_children(''):
            return
        if not self.sessionfile.closed:
            self.sessionfile.close()
        self.sessionfile = open(self.sessionpath, 'wb')
        items = self.main_tree.make_item_list()
        self.sessionfile.write(json.dumps(items, indent=2).encode("utf-8"))
        self.sessionfile.close()
    
    def saveas_session(self):
        if not self.main_tree.get_children(''):
            return
        filepath = filedialog.asksaveasfilename(initialfile="merlinator.json", filetypes=[('fichier json', '*.json')])
        if not filepath:
            return
        try:
            new_sessionfile = open(filepath, 'w')
            if self.sessionfile and not self.sessionfile.closed:
                self.sessionfile.close()
            self.sessionpath = filepath
            self.sessionfile = new_sessionfile
            self.save_session()
        except IOError:
            tk.messagebox.showwarning("Erreur", "Fichier non accessible") 

            
    def load_session(self):
        filepath = filedialog.askopenfilename(initialfile="merlinator.json", filetypes=[('fichier json', '*.json')])
        if not filepath:
            return
        try:
            file = open(filepath, 'r')
            self.sessionpath = filepath
            self.sessionfile = file
            items = json.loads(self.sessionfile.read())
            file.close()
            self.load_thumbnails(items)
            self.populate_trees(items)
        except IOError:
            tk.messagebox.showwarning("Erreur", "Fichier non accessible")        
        

        
    def make_main_tree(self, parent):
        self.main_tree = MerlinMainTree(parent, self)
        main_tree = self.main_tree
        main_tree.grid(row=0, column=0, sticky='nsew')
        
        self.scroll_my = tk.Scrollbar(parent, orient=tk.VERTICAL)
        self.scroll_my.grid(row=0, column=1, sticky=tk.N+tk.S)
        main_tree['yscrollcommand']=self.scroll_my.set
        self.scroll_my.config( command = main_tree.yview )
        self.scroll_mx = tk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.main_tree.xview)
        self.scroll_mx.grid(row=1, column=0, sticky=tk.E+tk.W)
        main_tree['xscrollcommand']=self.scroll_mx.set
        self.scroll_mx.config( command = main_tree.xview )
        
    
    def make_fav_tree(self, parent):
        self.fav_tree = MerlinFavTree(parent, self)
        fav_tree = self.fav_tree

        fav_tree.grid_rowconfigure(0, weight=1)
        fav_tree.grid_columnconfigure(0, weight=1)
        fav_tree.grid(row=0, column=0, sticky='nsew')

        self.scroll_fy = tk.Scrollbar(parent, orient=tk.VERTICAL)
        self.scroll_fy.grid(row=0, column=1, sticky=tk.N+tk.S)
        fav_tree['yscrollcommand']=self.scroll_fy.set
        self.scroll_fy.config( command = fav_tree.yview )
        self.scroll_fx = tk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.fav_tree.xview)
        self.scroll_fx.grid(row=1, column=0, sticky=tk.E+tk.W)
        fav_tree['xscrollcommand']=self.scroll_fx.set
        self.scroll_fx.config( command = fav_tree.xview )
        


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
    
        elif w == self.fav_tree:
            selected_node = w.selection()
            if selected_node and self.main_tree.selection() != selected_node:
                self.main_tree.selection_set(selected_node)
                self.main_tree.see(selected_node)
        else:
            return
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, self.main_tree.item(self.main_tree.selection(),'text')[3:])

    def clear_temp_variables(self, event):
        self.moveitem.set('')
        self.src_widget = None

    def movemouse(self,event):
        t = event.widget
        n = t.selection()
        self.src_widget = t
        self.moveitem.set(t.focus())
        x = event.x
        y = event.y
        # mitem.geometry("%dx%d+%d+%d" % (20, 10, x, y+90))
        # mitem.deiconify()
        self.save_cursor = t['cursor'] or ''
        if self.moveitem.get():
            t['cursor'] = "hand2"
            
    
    def mouserelease(self, event):
        t = event.widget
        t['cursor'] = self.save_cursor
        moveitem = self.moveitem
        src = moveitem.get()
        new_pos = None
        if src: 
            if t == self.src_widget:
                if t == self.main_tree:
                    if t.identify_region(event.x, event.y) == "tree":
                        dest = t.identify_row(event.y)
                    elif t.identify_column(event.x) == '#0':
                        dest = ''
                        if event.y<0 or (t.identify_region(event.x, event.y) in ["heading", "separator"]):
                            new_pos = 0
                        else:
                            new_pos = 'end'
                    else:
                        dest = src
                    if new_pos is None:
                        if t.set(dest, "type") in ['4', '36']: # destination is a file
                            if t.parent(dest)==t.parent(src) and t.index(dest)>=t.index(src):
                                new_pos = t.index(dest)
                            else:
                                new_pos = t.index(dest)+1
                            dest = t.parent(dest)
                        else:
                            new_pos = 0
                    
                    if src in t.get_ancestors(dest): # destination is descendant of source
                        pass
                    elif t.set(src, "type") in ['4', '36']: # source is a file
                        if src==dest:
                            pass
                        t.move(src, dest, new_pos)
                        t.see(src)
                    elif t.set(src, "type") in ['2', '34']: # source is a directory
                        iid = t.insert(dest, new_pos, text=t.item(src, "text"),
                                      values=t.item(src, "values"), image=t.item(src, "image"), 
                                      tags=t.item(src, "tags"))
                        t.set_children(iid, *t.get_children(src))
                        t.delete(src)
                        t.see(iid)
                    else: # shouldn't happen
                        pass
                elif t == self.fav_tree:
                    if t.identify_region(event.x, event.y) == "tree":
                        new_pos = t.index(t.identify_row(event.y))
                    elif t.identify_column(event.x) == '#0':
                        if event.y<0 or (t.identify_region(event.x, event.y) in ["heading", "separator"]):
                            new_pos = 0
                        else:
                            new_pos = 'end'
                    if new_pos is not None:
                        self.fav_tree.move(src, '', new_pos)
            elif self.src_widget == self.main_tree and t == self.fav_tree:
                
                if t.identify_region(event.x, event.y) == "tree":
                    new_pos = t.index(t.identify_row(event.y))
                elif t.identify_column(event.x) == '#0':
                    if event.y<0 or (t.identify_region(event.x, event.y) in ["heading", "separator"]):
                        new_pos = 0
                    else:
                        new_pos = 'end'
                if new_pos is not None:
                    self.main_tree.addToFavorite(src, new_pos)
                self.src_widget.update()
        t.update()
        moveitem.set("")
        self.src_widget = None

    
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
        

