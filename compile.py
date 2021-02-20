# -*- coding: utf-8 -*-
'''
Ce script permet de compiler les fichiers .ui et .qrc (ressources) en Python dans le dossier courant et le sous-dossier "forms".
Pour l'utiliser, dans le shell OSGeo4W de QGIS, faire un cd <chemin vers le dossier contenant compile.py> puis exécuter la commande "python compile.py".
'''

import glob
import os
import subprocess

# ui_files = glob.glob('*.ui')
# for ui in ui_files:
#     (name, ext) = os.path.splitext(ui)
#     print ("pyuic5.bat -o {}.py {}".format(name, ui))
#     subprocess.call(["pyuic5.bat", "-o", "{}.py".format(name), ui])

rc_files = glob.glob('*.qrc')
for rc in rc_files:
    (name, ext) = os.path.splitext(rc)
    print ("pyrcc5.bat -o {}.py {}".format(name, rc))
    subprocess.call(["pyrcc5.bat", "-o", "{}.py".format(name), rc])

pro_files = glob.glob('*.pro')
for pro in pro_files:
    (name, ext) = os.path.splitext(pro)
    print ("pylupdate5.bat {}".format(pro))
    subprocess.call(["pylupdate5.bat"])
    subprocess.call(["pylupdate5.bat", "{}".format(pro)])

qm_files = glob.glob('*.ts')
for qm in qm_files:
    (name, ext) = os.path.splitext(qm)
    print ("lrelease {}".format(qm))
    subprocess.call(["lrelease"])
    subprocess.call(["lrelease", "{}".format(qm)])
