# ImageCompressor

**ImageCompressor** Est une application graphique macOS simple développée en Python avec Tkinter qui permet de compresser des images (JPEG, PNG) individuellement ou par lot tout en préservant la qualité.

---

## Fonctionnalités

- Compression d’une image unique ou d’un dossier complet contenant des images JPEG et PNG.
- Réduction significative de la taille des fichiers sans perte visible de qualité.
- Interface graphique simple avec réglage du taux de compression (qualité).
- Les images compressées sont sauvegardées dans un dossier `compressed` à côté des originaux.
- Application packagée en `.app` macOS avec py2app (option icône personnalisée).

---

## Compiler via le terminal 

- python3 setup.py py2app
./dist/ImageCompressor.app/Contents/MacOS/ImageCompressor


## Compiler via le double-clic 
- python3 setup.py py2app

- Dans le Finder, ouvre le dossier dist et double-clique sur ImageCompressor.app pour lancer l’application.


## Prérequis

- macOS (Catalina ou version ultérieure recommandée)
- Python 3 installé ([python.org](https://www.python.org/downloads/mac-osx/))
- Modules Python : Pillow, py2app  = > installation rapid via le terminal pip3 install pillow
et pip3 install py2app
- chmod +x image_compressor_gui.py

- git clone https://github.com/mimpungu/image_compressor.git



Installe les modules requis via pip :

```bash
pip install pillow py2app

## Compiler via le terminal 

- python3 setup.py py2app
./dist/ImageCompressor.app/Contents/MacOS/ImageCompressor


## Compiler via le double-clic 
- python3 setup.py py2app

- Dans le Finder, ouvre le dossier dist et double-clique sur ImageCompressor.app pour lancer l’application.

