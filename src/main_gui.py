# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.


import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from PIL import Image
from PIL.ImageTk import PhotoImage
import os.path, zipfile

from io_utils import *
from treeviews import MerlinMainTree, MerlinFavTree
from gui_actions import *
try:
    from audio import AudioWidget
    enable_audio = True
except ImportError as error:
    enable_audio = False

class MerlinGUI(GUIActions):
    
    def __init__(self):
        # create root window
        tk.Tk.__init__(self)
        self.title('Merlinator')
        # self.iconbitmap("../res/merlinator_64px.ico")
        self.load_image()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.sessionpath = ''
        self.sessionfile = None
        self.thumbnails = {}
        self.moveitem = tk.StringVar()
        self.src_widget = None
        self.save_cursor = self['cursor'] or ''
        self.enable_audio = enable_audio


        
        # configure the grid layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.maxsize(width=screen_w, height=screen_h)
        # rw = int(screen_w / 2)
        # rh = int(screen_h / 2)
        # self.geometry('{}x{}+{:g}+{:g}'.format(rw, rh, rw / 2, rh / 2))
        self.geometry('{}x{}+{:g}+{:g}'.format(800, 600, 300, 100))
        self.update()
        
        # Create menu
        top_menu = tk.Menu(self)
        self.config(menu=top_menu)
        file_menu = tk.Menu(top_menu, tearoff=False)
        top_menu.add_cascade(label='Fichier', underline=0, menu=file_menu)
        file_menu.add_command(label="Nouvelle session (Ctrl-n)", underline=0, command=self.new_session)
        file_menu.add_command(label="Ouvrir session (Ctrl-o)", underline=0, command=self.load_session)
        file_menu.add_command(label="Sauver session  (Ctrl-s)", underline=0, command=self.save_session)
        file_menu.add_command(label="Sauver session sous", underline=1, command=self.saveas_session)
        file_menu.add_separator()
        file_menu.add_command(label="Importer playlist/archive (Ctrl-i)", underline=0, command=self.import_playlist)
        file_menu.add_command(label="Exporter playlist (Ctrl-e)", underline=0, command=self.export_playlist)
        file_menu.add_command(label="Exporter archive (Ctrl-x)", underline=1, command=self.export_all_to_zip)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", underline=0, command=self.quit)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Main paned window
        self.main_paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned_window.grid(row=0, column=0, sticky='eswn')
        
        # Main tree area
        self.main_tree_area = tk.LabelFrame(self.main_paned_window, text="Playlist", width=450)
        self.main_tree_area.grid_rowconfigure(0, weight=1)
        self.main_tree_area.grid_columnconfigure(0, weight=1)
        self.main_tree_area.grid_propagate(0)
        self.main_paned_window.add(self.main_tree_area)
        
        style = ttk.Style()
        style.configure("Treeview", rowheight=40)        
        self.update()
        
        self.make_main_tree(self.main_tree_area)
        
        # Control Frame
        self.control_frame = tk.Frame(self.main_paned_window, width=330)
        self.control_frame.grid_rowconfigure(4, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)
        self.control_frame.grid_propagate(0)
        self.main_paned_window.add(self.control_frame, sticky="nsew")
        
        # Title / Sound 
        self.title_label_frame = tk.LabelFrame(self.control_frame, text="Contenu", height=2, padx=5)
        self.title_label_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        self.title_label_frame.grid_columnconfigure(0, weight=1)
        vcmd = (self.register(lambda s: len(s.encode('UTF-8'))<=66), '%P')
        self.title_entry = tk.Entry(self.title_label_frame, state='disabled', validate='key', validatecommand=vcmd)
        self.title_entry.grid(row=0, column=0, sticky='ew')
        self.title_entry.bind('<Return>', self.setTitle)
        self.buttonSetTitle = tk.Button(self.title_label_frame, text="Mettre à jour le titre",fg="black", command=self.setTitle, state='disabled')
        self.buttonSetTitle.grid(row=1, column=0)
        self.title_entry.bind('<KeyRelease>', self.sync_title_button)

        # Audio
        if self.enable_audio:
            self.audio_widget = AudioWidget(self.title_label_frame, self)
            self.audio_widget.grid(row=2, column=0, sticky = 'ew')
            self.bind("<space>", self.audio_widget.PlayPause)
        
        
        
        # Edition Area
        self.edition_area = tk.LabelFrame(self.control_frame, text='Édition')
        self.edition_area.grid(row=2, column=1, sticky='en')
        
        self.buttonDelete = tk.Button(self.edition_area, text="Supprimer", state='disabled', command=self.main_tree.deleteNode)
        self.buttonSelectImage = tk.Button(self.edition_area, text="Changer image", state='disabled', command=self.main_tree.select_image)
        self.buttonAddMenu = tk.Button(self.edition_area, text="Nouveau Menu", state='disabled', command=self.main_tree.add_menu)
        self.buttonAddSound = tk.Button(self.edition_area, text="Nouveau Son", state='disabled', command=self.main_tree.add_sound)
                
        self.buttonSelectImage.grid(row=0, column=1, sticky='ew')
        self.buttonDelete.grid(row=1, column=1, sticky='ew')
        self.buttonAddMenu.grid(row=0, column=0, sticky='ew')
        self.buttonAddSound.grid(row=1, column=0, sticky='ew')
        
        
        # Displacement Buttons
        self.main_tree_button_area = tk.LabelFrame(self.control_frame, text='Déplacer\nélément', width=60)
        self.main_tree_button_area.grid(row=2, column=0, sticky='nw')
        
        self.buttonMoveUp = tk.Button(self.main_tree_button_area, text="\u21D1", width=8, state='disabled', command=self.main_tree.moveUp)
        self.buttonMoveUp.grid(row=0, column=0)
        self.buttonMoveParentDir = tk.Button(self.main_tree_button_area, text="\u21D0", width=8, state='disabled', command=self.main_tree.moveParentDir)
        self.buttonMoveParentDir.grid(row=1, column=0)
        self.buttonMoveDown = tk.Button(self.main_tree_button_area, text="\u21D3", width=8, state='disabled', command=self.main_tree.moveDown)
        self.buttonMoveDown.grid(row=2, column=0)
         
         
        # Favorite tree area
        self.fav_tree_area = tk.LabelFrame(self.control_frame, text="Favoris", width=200)
        self.fav_tree_area.grid_rowconfigure(0, weight=1)
        self.fav_tree_area.grid_columnconfigure(0, weight=1)
        self.fav_tree_area.grid(row=4, column=0, columnspan=2, sticky='nsew')
        self.fav_tree_area.grid_propagate(0)
        self.make_fav_tree(self.fav_tree_area)
        
        #Favorite Button
        self.buttonToggleFavorite = tk.Button(self.control_frame, text="Ajouter/retirer\ndes favoris", state='disabled', command=self.main_tree.toggleFavorite)
        self.buttonToggleFavorite.grid(row=3, column=0, sticky='sw')
        
        self.fav_tree_button_area = tk.LabelFrame(self.control_frame, text='Déplacer favori')
        self.fav_tree_button_area.grid(row=3, column=1, sticky='s')
        self.buttonMoveUpFav = tk.Button(self.fav_tree_button_area, text="\u21D1",fg="black", width=8, state='disabled', command=self.fav_tree.moveUp)
        self.buttonMoveUpFav.grid(row=0, column=0)
        self.buttonMoveDownFav = tk.Button(self.fav_tree_button_area, text="\u21D3",fg="black", width=8, state='disabled', command=self.fav_tree.moveDown)
        self.buttonMoveDownFav.grid(row=0, column=1)
        
        
        self.update()
        
        
        self.bind("<BackSpace>", self.main_tree.deleteNode)
        self.bind("<Delete>", self.main_tree.deleteNode)
        
        self.bind("<Control-o>", lambda event:self.load_session())
        self.bind("<Control-s>", lambda event:self.save_session())
        self.bind("<Control-n>", lambda event:self.new_session())
        self.bind("<Control-i>", lambda event:self.import_playlist())
        self.bind("<Control-e>", lambda event:self.export_playlist())
        self.bind("<Control-x>", lambda event:self.export_all_to_zip())


        
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
        

    def populate_trees(self, items, overwrite):
        self.main_tree.populate(items, self.thumbnails, overwrite)
        self.fav_tree.populate(self.main_tree, overwrite)
        

    def load_thumbnails(self, items, overwrite=True):
        if overwrite:
            self.thumbnails = {}
        for item in items:
            imagepath = item['imagepath']
            if item['uuid'] in self.thumbnails:
                continue
            if os.path.exists(imagepath):
                with Image.open(imagepath) as image:
                    image_small = image.resize((40, 40), Image.ANTIALIAS)
                    self.thumbnails[item['uuid']] = PhotoImage(image_small)
            else:
                self.thumbnails[item['uuid']] = ''
                
    
    def load_thumbnails_from_zip(self, items, zfile, overwrite=True):
        if overwrite:
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
                
    def load_image(self):
        filename = "merlinator_64px.ico"
        with zipfile.ZipFile('../res/defaultPics.zip', 'r') as zfile:
            zippath = zipfile.Path(zfile, at=filename)
            if zippath.exists():
                with zfile.open(filename, 'r', pwd=info) as imagefile:
                    with Image.open(imagefile) as image:
                        self.iconphoto(False, PhotoImage(image))



    def import_playlist(self):
        filepath = filedialog.askopenfilename(initialfile="playlist.bin", filetypes=[('tous types supportés', '*.bin;*.zip'), ('binaire', '*.bin'), ('fichier zip', '*.zip')])
        if not filepath:
            return
        
        overwrite = True
        if self.main_tree.get_children():
            dialog = TwoButtonCancelDialog(title="Combiner ou écraser?", parent=self, \
                                            prompt="Écraser la playlist courante, ou combiner les playlists?", \
                                            button0text="Combiner", button1text="Écraser")
            if dialog.res == 2:
                return
            elif dialog.res == 0:
                overwrite = False
    
        try: 
            if filepath[-3:] == "bin":
                dirname = os.path.dirname(filepath)
                with open(filepath, "rb") as file:
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
                    self.load_thumbnails(items, overwrite)
            elif filepath[-3:] == "zip":
                with zipfile.ZipFile(filepath, 'r') as z:
                    with z.open("playlist.bin", "r") as file:
                        items = read_merlin_playlist(file)
                    for item in items:
                        item['imagepath'] = filepath
                        if item['type'] in [4, 36]:
                            item['soundpath'] = filepath
                        else:
                            item['soundpath'] = ''
                    self.load_thumbnails_from_zip(items, z, overwrite)
            self.populate_trees(items, overwrite)
            self.buttonAddMenu['state'] = 'normal'
            self.buttonAddSound['state'] = 'normal'
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
        self.buttonAddMenu['state'] = 'normal'
        self.buttonAddSound['state'] = 'normal'
        
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
            self.buttonAddMenu['state'] = 'normal'
            self.buttonAddSound['state'] = 'normal'
        except IOError:
            tk.messagebox.showwarning("Erreur", "Fichier non accessible")        
        

        
    def clear_temp_variables(self, event=None):
        self.moveitem.set('')
        self.src_widget = None

    def mouseclick(self, event):
        t = event.widget
        if t.identify_region(event.x, event.y) == "tree":
            self.moveitem.set(t.identify_row(event.y))

    def movemouse(self, event):
        t = event.widget
        self.src_widget = t
        # self.moveitem.set(t.focus())
        self.save_cursor = t['cursor'] or ''
        if self.moveitem.get():
            t['cursor'] = "hand2"
            
    
    def mouserelease(self, event):
        t = event.widget
        t['cursor'] = self.save_cursor
        
        x = event.x+t.winfo_rootx()
        y = event.y+t.winfo_rooty()
        x0 = self.main_tree.winfo_rootx()
        x1 = x0 + self.main_tree.winfo_width()
        y0 = self.main_tree.winfo_rooty()
        y1 = y0 + self.main_tree.winfo_height()
        if x0<=x<=x1 and y0<=y<=y1:
            t = self.main_tree
        else:
            x0 = self.fav_tree.winfo_rootx()
            x1 = x0 + self.fav_tree.winfo_width()
            y0 = self.fav_tree.winfo_rooty()
            y1 = y0 + self.fav_tree.winfo_height()
            if x0<=x<=x1 and y0<=y<=y1:
                t = self.fav_tree
            else:
                t = None
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
                    self.sync_buttons_main()
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
                    self.sync_buttons_main()
            elif self.src_widget == self.main_tree and t == self.fav_tree:
                dest_x = event.x+event.widget.winfo_rootx()-t.winfo_rootx()
                dest_y = event.y+event.widget.winfo_rooty()-t.winfo_rooty()
                if t.identify_region(dest_x, dest_y) == "tree":
                    new_pos = t.index(t.identify_row(dest_y))+1
                elif t.identify_column(dest_x) == '#0':
                    if event.y<0 or (t.identify_region(dest_x, dest_y) in ["heading", "separator"]):
                        new_pos = 0
                    else:
                        new_pos = 'end'
                if new_pos is not None:
                    self.main_tree.addToFavorite(src, new_pos)
                self.src_widget.update()
                self.sync_buttons_fav()
        t.update()
        moveitem.set("")
        self.src_widget = None

    
        


