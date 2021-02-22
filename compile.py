# -*- coding: utf-8 -*-
"""
Ce script permet de compiler les fichiers .ui et .qrc (ressources) en Python dans le dossier courant et le sous-dossier "forms".
Pour l'utiliser, dans le shell OSGeo4W de QGIS, faire un cd <chemin vers le dossier contenant compile.py> puis exécuter la commande "python compile.py".
"""

import glob
import os
import subprocess
import datetime


def compile_ui_qrc():
    # Compile .ui files
    # ui_files = glob.glob('*.ui')
    # for ui in ui_files:
    #     (name, ext) = os.path.splitext(ui)
    #     print ("pyuic5.bat -o {}.py {}".format(name, ui))
    #     subprocess.call(["pyuic5.bat", "-o", "{}.py".format(name), ui])

    # Compile .qrc ressources file
    rc_files = glob.glob('*.qrc')
    for rc in rc_files:
        (name, ext) = os.path.splitext(rc)
        print("pyrcc5.bat -o {}.py {}".format(name, rc))
        subprocess.call(["pyrcc5.bat", "-o", "{}.py".format(name), rc])


def convert_pro():
    # Creation of .ts files from .pro file
    if not glob.glob('*.pro'):
        # Find the plugin class name
        plugin_dir = os.getcwd()
        f = open("{}/__init__.py".format(plugin_dir), "r")
        init_file = f.read()
        f.close()
        class_name = ""
        for line in init_file.split("\n"):
            if "return" in line:
                start = line.find("return") + len("return")
                end = line.find("(iface)")
                class_name = line[start+1:end]

        # Find all .ui files
        ui_files = glob.glob("{}/**/*.ui".format(plugin_dir), recursive=True)
        str_pro_ui = ""
        for ui in ui_files:
            pro_ui = ui.replace(plugin_dir, " ..")
            str_pro_ui += pro_ui

        # Find all .py files
        py_files = glob.glob("{}/**/*.py".format(plugin_dir), recursive=True)
        str_pro_py = ""
        list_ignore_py = [" ..\\compile.py", " ..\\resources.py", " ..\\__init__.py"]
        for py in py_files:
            pro_py = py.replace(plugin_dir, " ..")
            str_pro_py += pro_py
            if "_dialog.py" in pro_py:
                list_ignore_py.append(pro_py)

        for ignore in list_ignore_py:
            str_pro_py = str_pro_py.replace(ignore, "")

        if str_pro_ui != "" and str_pro_py != "" and class_name != "":
            pro_string = "FORMS ={} \nSOURCES ={} \nTRANSLATIONS = {}_fr.ts".format(str_pro_ui, str_pro_py, class_name)
            f = open("{}/i18n/{}.pro".format(plugin_dir, class_name), "w")
            f.write(pro_string)
            f.close()
        else:
            print("Error")
    else:
        pass

    pro_files = glob.glob('i18n/*.pro')
    for pro in pro_files:
        print("pylupdate5.bat {}".format(pro))
        subprocess.call(["pylupdate5.bat"])
        subprocess.call(["pylupdate5.bat", "{}".format(pro)])


def convert_ts():
    # If translation is done, create .qm files from the .ts files
    pro_files = glob.glob('i18n/*.pro')
    ts_files = glob.glob('i18n/*.ts')
    pro_mtime = os.path.getmtime(pro_files[0])
    ts_mtime = os.path.getmtime(ts_files[0])
    print(ts_mtime-pro_mtime)
    print(datetime.datetime.fromtimestamp(pro_mtime))

    qm_files = glob.glob('*.ts')
    for qm in qm_files:
        print("lrelease {}".format(qm))
        # subprocess.call(["lrelease", "{}".format(qm)])


if __name__ == "__main__":
    compile_ui_qrc()
    convert_pro()
    convert_ts()
