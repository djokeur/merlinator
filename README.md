# merlinator

Playlist editor for the Merlin children loudspeaker from La Chouette Radio (Bayard / Radio France)

Merlinator est un éditeur de playlist pour l'enceinte Merlin de La Chouette Radio (Bayard/ Radio France).

## Comment utiliser merlinator ?

### Préliminaire : accéder à la carte micro-sd

Ouvrir la Merlin en dévissant les 4 vis dans le dos de l'enceinte. Sur le circuit imprimé principal, un emplacement pour carte micro-SD est accessible. Pour libérer la carte, pousser dessus comme pour l'enfoncer un peu plus dans le lecteur. Vous pouvez maintenant la retirer. La carte est normalementz lisible sur n'importe quel lecteur de micro-SD. En particulier, on peu la mettre dans un téléphone portable pour accéder directement à son contenu.

### Installation

Merlinator nécessite Python (il a été écrit et testé sur la version 3.10 de python, mais il est probablement compatible avec d'autres versions). Python est disponible librement pour de nombreuses plateformes, en particulier Windows, MacOS ou Linux. Voir [https://python.org/downloads/](https://python.org/downloads/) pour télécharger python. En plus des bibliothèques standard de python, merlinator nécessite la bibliothèque 'Pillow'.

Pour installer Pillow, taper dans une invite de commande les lignes suivantes :

    python -m pip install --upgrade pip
    python -m pip install --upgrade Pillow

Pour bénéficier de la fonction de lecture audio (optionnelle), merlinator a besoin des bibliothèques 'pygame' et 'mutagen', disponibles elles aussi librement. Pour les installer, taper simplement les commandes suivantes :

    python -m pip install pygame
    python -m pip install mutagen

### Lancement

Après avoir téléchargé les fichiers de merlinator, double-cliquer sur le fichier 'merlinator.py' dans le sous-dossier 'src'. Vous pouvez aussi taper 'python merlinator.py' dans une invite de commande depuis ce sous-dossier.

### Utilisation

Pour lire la playlist de la Merlin, placer tout d'abord la carte micro-SD dans un lecteur connecté à l'ordinateur. Un téléphone portable équipé d'un emplacement micro-SD peut parfaitement jouer ce rôle. Dans le menu 'fichier' de merlinator, cliquer sur 'Importer playlist' et sélectionner le fichier 'playlist.bin', dans le dossier-racine de la carte micro-SD. Vous pouvez maintenant éditer cette playlist, en ajoutant des menus ou des sons grâces aux boutons correspondant sur l'interface graphique. 

Pour lire cette playlist modifiée, cliquer sur 'Fichier/Exporter playlist' et sauvegarder le fichier sous le nom 'playlist.bin'. Placer ensuite ce fichier ainsi que les images et fichiers sons correspondant dans le dossier racine de la carte micro-SD. Replacer la carte dans la Merlin, et c'est parti !

Merlinator peut aussi créer une archive zip contenant tout les fichiers à placer dans la carte micro-SD (playlist, images et sons). Pour cela, cliquer sur 'Fichier/Exporter archive'.

**ATTENTION** : penser à faire une sauvegarde du contenu initial de la carte micro-SD avant les modifications ! On ne sait jamais ce qui peut arriver, et merlinator n'a pas de fonction 'annuler' !

### Important : format des fichiers

- La playlist en tant que telle est le fichier nommé 'playlist.bin', qui doit se trouver dans le dossier racine de la carte micro-SD de la Merlin.
- Les fichiers sons et images doivent aussi se trouver dans le même dossier.
- Les extensions des noms de fichiers doivent être '.mp3' pour les sons et '.jpg' pour les images.
- Pour s'afficher sur l'enceinte, une image doit avoir le même nom de fichier (à l'exception de l'extension) que le son correspondant.
- Les noms de fichiers sont limités à 64 octets en encodage utf-8 (compter un octet par caractère simple et deux par caractère accentué).
- D'après mes observations, les fichiers images sont au format jpeg avec une résolution de 128x128, et les sons sont au format mp3 en stéréo à 128ko/s. Je sais pas si d'autres formats sont supportés. En revanche, les images au format "progressive JPEG" ne sont pas supportées par toutes les versions de l'enceinte.

Dans sa version actuelle, merlinator crée le fichier de playlist, mais ne vérifie pas si toutes les conditions mentionnée ci-dessus sont remplies.
