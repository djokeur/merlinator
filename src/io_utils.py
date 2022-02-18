# Copyright 2022 by Cyril Joder.
# All rights reserved.
# This file is part of merlinator, and is released under the 
# "MIT License Agreement". Please see the LICENSE file
# that should have been included as part of this package.


from tkinter import Tk, filedialog, messagebox
from PIL import Image
from PIL.ImageTk import PhotoImage
import zipfile
import os.path
import json


bytezero = b'\x00'
info = b"ChouetteRadio"


def read_merlin_playlist(stream):

    items = []
    byte = stream.read(1)
    while byte:
        
        item = dict()
        # id
        b = byte + stream.read(1)
        if not b: raise Exception("wrong file format")
        item['id'] = int.from_bytes(b, byteorder='little')
        
        # id du parent
        b = stream.read(2)
        if not b: raise Exception("wrong file format")
        item['parent_id'] = int.from_bytes(b, byteorder='little')
        
        # ordre
        b = stream.read(2)
        if not b: raise Exception("wrong file format")
        item['order'] = int.from_bytes(b, byteorder='little')
        
        # nb_enfants
        b = stream.read(2)
        if not b: raise Exception("wrong file format")
        item['nb_children'] = int.from_bytes(b, byteorder='little')
        
        # ordre dans les favoris
        b = stream.read(2)
        if not b: raise Exception("wrong file format")
        item['fav_order'] = int.from_bytes(b, byteorder='little')
        
        # type d'item
        b = stream.read(2)
        if not b: raise Exception("wrong file format")
        item['type'] = int.from_bytes(b, byteorder='little')
        
        # date limite
        b = stream.read(4)
        if not b: raise Exception("wrong file format")
        item['limit_time'] = int.from_bytes(b, byteorder='little')
        
        # date d'ajout
        b = stream.read(4)
        if not b: raise Exception("wrong file format")
        item['add_time'] = int.from_bytes(b, byteorder='little')
        
        # uuid (nom de fichier)
        b = stream.read(1)
        if not b: raise Exception("wrong file format")
        length = int.from_bytes(b, byteorder='little')
        b = stream.read(length)
        item['uuid'] = b.decode('UTF-8')
        b = stream.read(64-length)
        
        # titre
        b = stream.read(1)
        if not b: raise Exception("wrong file format")
        length = int.from_bytes(b, byteorder='little')
        b = stream.read(length)
        item['title'] = b.decode('UTF-8')
        b = stream.read(66-length)
        
        items.append(item)
        byte = stream.read(1)
    return items



def write_merlin_playlist(stream, items):
    
    for item in items:

        # id
        b = item['id'].to_bytes(2,byteorder='little')
        stream.write(b)
        
        # id du parent
        b = item['parent_id'].to_bytes(2, byteorder='little')
        stream.write(b)
        
        # ordre
        b = item['order'].to_bytes(2, byteorder='little')
        stream.write(b)
        
        # nb_enfants
        b = item['nb_children'].to_bytes(2, byteorder='little')
        stream.write(b)
        
        # ordre dans les favoris
        b = item['fav_order'].to_bytes(2, byteorder='little')
        stream.write(b)
        
        # type d'item
        b = item['type'].to_bytes(2, byteorder='little')
        stream.write(b)
        
        # date limite
        b = item['limit_time'].to_bytes(4, byteorder='little')
        stream.write(b)
        
        # date d'ajout
        b = item['add_time'].to_bytes(4, byteorder='little')
        stream.write(b)
        
        # uuid (nom de fichier)
        b = item['uuid'].encode('UTF-8')
        length = len(b)
        length_b = length.to_bytes(1, byteorder='little')
        stream.write(length_b)
        stream.write(b)
        stream.write(bytezero*(64-length))
        
        # titre
        b = item['title'].encode('UTF-8')
        length = len(b)
        length_b = length.to_bytes(1, byteorder='little')
        stream.write(length_b)
        stream.write(b)
        stream.write(bytezero*(66-length))
    
def format_item(item):
    for key in ("fav_order", "type", "limit_time", "add_time", "nb_children"):
        if type(item[key]) is not int:
            if item[key]:
                item[key] = int(item[key])
            else:
                item[key] = 0
    return item
       
    

def export_merlin_to_zip(items, zfile):
    files_not_found = []        
    for item in items:
        imagepath = item['imagepath']
        if imagepath:
            filename = item['uuid'] + '.jpg'
            outfilezippath = zipfile.Path(zfile, at=filename)
            if not outfilezippath.exists():
                if imagepath[-4:] == '.jpg':
                    if os.path.exists(imagepath):
                        with Image.open(imagepath) as image:
                            image_icon = image.resize((128,128), Image.ANTIALIAS)
                            with zfile.open(filename, "w") as fout:
                                image_icon.save(fout, "JPEG", mode='RGB')
                    else:
                        files_not_found.append(imagepath)
                else:
                    try:
                        with zipfile.ZipFile(imagepath, "r") as zin:
                            with zfile.open(filename, "w") as fout:
                                fout.write(zin.read(filename, pwd=info))
                    except IOError:
                        files_not_found.append(item['uuid'] + '.jpg')

        soundpath = item['soundpath']
        if soundpath:
            filename = item['uuid'] + '.mp3'
            outfilezippath = zipfile.Path(zfile, at=filename)
            if not outfilezippath.exists():
                if soundpath[-4:] == '.mp3':
                    if os.path.exists(soundpath):
                        zfile.write(soundpath, filename)
                    else:
                        file_not_found.append(soundpath)
                else:
                    try:
                        with zipfile.ZipFile(soundpath, "r") as zin:
                            with zfile.open(filename, "w") as fout:
                                fout.write(zin.read(filename, pwd=info))
                    except IOError:
                        files_not_found.append(filename)
    with zfile.open("playlist.bin", "w") as fout:
        write_merlin_playlist(fout, items)
    
    return files_not_found
        
