from setuptools import setup

APP = ['image_compressor_gui.py']
OPTIONS = {
    'argv_emulation': False,             # Désactivé pour macOS Catalina et + (évite l’erreur Carbon)
    'iconfile': 'icon.icns',             # Remplace par le nom de ton fichier icône .icns ou None
    'packages': ['PIL'],
    'includes': ['PIL._tkinter_finder'],  # Aide py2app à trouver PIL + tkinter
    'plist': {
        'CFBundleName': 'ImageCompressor',
        'CFBundleDisplayName': 'ImageCompressor',
        'CFBundleIdentifier': 'com.example.imagecompressor',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
