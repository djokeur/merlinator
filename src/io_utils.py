# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.

import tkinter as tk
from tkinter import filedialog
import os.path

bytezero = b'\x00'



def read_merlin_playlist(filepath=None):

    items = []    
    if filepath is None:
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(initialfile="playlist.bin", filetypes=[('binary', '*.bin')])
    try:
        with open(filepath, "rb") as file:
            byte = file.read(1)
            while byte:
                item = read_merlin_item(byte, file)
                items.append(item)
                byte = file.read(1)
            file.close()
    except IOError:
        print("File not accessible")
    directory = os.path.dirname(filepath)
    return items, filepath

def read_merlin_item(first_byte, file):
    
    item = dict()
    # id
    b = first_byte + file.read(1)
    if not b: raise Exception("wrong file format")
    item['id'] = int.from_bytes(b, byteorder='little')
    
    # id du parent
    b = file.read(2)
    if not b: raise Exception("wrong file format")
    item['parent_id'] = int.from_bytes(b, byteorder='little')
    
    # ordre
    b = file.read(2)
    if not b: raise Exception("wrong file format")
    item['order'] = int.from_bytes(b, byteorder='little')
    
    # nb_enfants
    b = file.read(2)
    if not b: raise Exception("wrong file format")
    item['nb_children'] = int.from_bytes(b, byteorder='little')
    
    # ordre dans les favoris
    b = file.read(2)
    if not b: raise Exception("wrong file format")
    item['fav_order'] = int.from_bytes(b, byteorder='little')
    
    # type d'item
    b = file.read(2)
    if not b: raise Exception("wrong file format")
    item['type'] = int.from_bytes(b, byteorder='little')
    
    # date limite
    b = file.read(4)
    if not b: raise Exception("wrong file format")
    item['limit_time'] = int.from_bytes(b, byteorder='little')
    
    # date d'ajout
    b = file.read(4)
    if not b: raise Exception("wrong file format")
    item['add_time'] = int.from_bytes(b, byteorder='little')
    
    # uuid (nom de fichier)
    b = file.read(1)
    if not b: raise Exception("wrong file format")
    length = int.from_bytes(b, byteorder='little')
    b = file.read(length)
    item['uuid'] = b.decode('UTF-8')
    b = file.read(64-length)
    
    # titre
    b = file.read(1)
    if not b: raise Exception("wrong file format")
    length = int.from_bytes(b, byteorder='little')
    b = file.read(length)
    item['title'] = b.decode('UTF-8')
    b = file.read(66-length)
    
    return item


def write_merlin_playlist(items, filepath=None):
    
    if filepath is None:
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.asksaveasfilename(initialfile="playlist.bin", filetypes=[('binary', '*.bin')])
    
    try:
        with open(filepath, "wb") as file:
            for item in items:
                write_merlin_item(item, file)
            file.close()
    except IOError:
        print("File not accessible")
        


def write_merlin_item(item, file):
    
    # id
    b = item['id'].to_bytes(2,byteorder='little')
    file.write(b)
    
    # id du parent
    b = item['parent_id'].to_bytes(2, byteorder='little')
    file.write(b)
    
    # ordre
    b = item['order'].to_bytes(2, byteorder='little')
    file.write(b)
    
    # nb_enfants
    b = item['nb_children'].to_bytes(2, byteorder='little')
    file.write(b)
    
    # ordre dans les favoris
    b = item['fav_order'].to_bytes(2, byteorder='little')
    file.write(b)
    
    # type d'item
    b = item['type'].to_bytes(2, byteorder='little')
    file.write(b)
    
    # date limite
    b = item['limit_time'].to_bytes(4, byteorder='little')
    file.write(b)
    
    # date d'ajout
    b = item['add_time'].to_bytes(4, byteorder='little')
    file.write(b)
    
    # uuid (nom de fichier)
    b = item['uuid'].encode('UTF-8')
    length = len(b)
    length_b = length.to_bytes(1, byteorder='little')
    file.write(length_b)
    file.write(b)
    file.write(bytezero*(64-length))
    
    # titre
    b = item['title'].encode('UTF-8')
    length = len(b)
    length_b = length.to_bytes(1, byteorder='little')
    file.write(length_b)
    file.write(b)
    file.write(bytezero*(66-length))
    
    

def format_item(item):
    for key in ("fav_order", "type", "limit_time", "add_time", "nb_children"):
        if type(item[key]) is not int:
            item[key] = int(item[key])
    return item
       