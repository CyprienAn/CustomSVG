# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CustomSVG
                                 A QGIS plugin
 Plugin to allow customization of SVG symbols in QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-01-31
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Cyprien Antignac
        email                : antignac.cyprien+git@protonmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import Qgis

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .custom_svg_dialog import CustomSVGDialog
import os.path
import glob


class CustomSVG:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CustomSVG_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Custom SVG')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CustomSVG', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/custom_svg/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Adapts SVG to QGIS'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Custom SVG'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = CustomSVGDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Get the path of Input and Output directory
            input_directory = self.dlg.fdInputDirectory.filePath()
            output_directory = self.dlg.fdOutputDirectory.filePath()
            # Verify if Input and Output path exist
            if os.path.isdir(input_directory):
                if os.path.isdir(output_directory):
                    # If the paths exist we go to modify_svg()
                    self.modify_svg(input_directory, output_directory)
                else:
                    self.iface.messageBar().pushMessage("Error : ",
                                                        "Output directory does not exist !",
                                                        level=Qgis.Critical, duration=5)
            else:
                self.iface.messageBar().pushMessage("Error : ",
                                                    "Input directory does not exist !",
                                                    level=Qgis.Critical, duration=5)

    def modify_svg(self, dir_input, dir_output):
        """Find in the svg file the parts needed to make the symbols editable in QGIS.

         :param dir_input: Folder path where to find SVGs.
         :type dir_input: str, QString

         :param dir_output: Folder path where to save new SVGs.
         :type dir_output: str, QString
         """

        # Get all SVGs files in the Input folder
        svg_files = glob.glob("{}/*.svg".format(dir_input))
        svg_count = 0

        # Modify all SVGs one by one
        for svg in svg_files:
            svg_count += 1
            name = os.path.basename(svg)

            # Check if an SVG name start by "qgs_" exist and ignore him
            if name.startswith("qgs_"):
                pass

            else:
                # Get the code in the SVG
                svg_file = open("{}".format(svg), 'r')
                svg_code = svg_file.read()
                svg_file.close()

                # List of parameters that we have to adapt in the code
                dict_param = {"fill:": "param(fill) ",
                              "fill-opacity:": "param(fill-opacity) ",
                              "stroke:": "param(outline) ",
                              "stroke-opacity:": "param(outline-opacity) ",
                              "stroke-width:": "param(outline-width) ",
                              "fill=": "param(fill) ",
                              "fill-opacity=": "param(fill-opacity) ",
                              "stroke=": "param(outline) ",
                              "stroke-opacity=": "param(outline-opacity) ",
                              "stroke-width=": "param(outline-width) "
                              }

                # Define variables necessary for the smooth running of the loops
                search_path_tag = True  # When we have all path tag, it will change in False
                idx_start_path = 0
                idx_end_path = 0

                # While we haven't gone through all path tag, we search and treat the next tag path
                while search_path_tag:

                    # Verify if path tag exist in file
                    if idx_start_path != -1 or idx_end_path != -1:

                        # Index in the string of "<path"
                        idx_start_path = svg_code.find('<path', idx_end_path)

                        # Index in the string of the end of "<path", "/>" or "</path>"
                        idx_end_path = svg_code.find('/>', idx_start_path)
                        len_find = 2
                        if idx_end_path == -1:
                            idx_end_path = svg_code.find('</path>', idx_start_path)
                            len_find = 8

                        # Get the code between two indexes
                        old_path_tag = path_tag = svg_code[idx_start_path:idx_end_path + len_find]

                        # Replace all parameter in path tag
                        for param in dict_param:
                            # Start and End indexes in the string of the current parameter
                            idx_start_param = path_tag.find(param)
                            idx_end_param = path_tag.find(';', idx_start_param)

                            # Verify if current parameter exist in path tag
                            if idx_start_param != -1 and idx_end_param != -1:

                                # Extract the original value of parameter
                                old_tag = path_tag[idx_start_param:idx_end_param + 1]

                                path_tag = replace_parameter(old_tag, param, dict_param[param], path_tag)

                            # Verify if current parameter exist and if it's the last parameter in path tag
                            elif idx_start_param != -1 and idx_end_param == -1:

                                # Extract the original value of parameter
                                old_tag = path_tag[idx_start_param:idx_end_param]

                                path_tag = replace_parameter(old_tag, param, dict_param[param], path_tag)

                            # If the parameter does not exist in the path tag, we pass
                            else:
                                pass

                        # Replace the old path tag by the new one
                        svg_code = svg_code.replace(old_path_tag, path_tag)

                    # When we are at the end of the file, we change the "search_path_tag" value to exit "While"
                    else:
                        search_path_tag = False

                # Export of the new SVG
                output_path = "{}/qgs_{}".format(dir_output, name)
                output = open(output_path, "w")
                output.write(svg_code)
                output.close()

        # Message at the end of process
        self.iface.messageBar().pushMessage("Adapts SVG to QGIS",
                                            "{} adapted SVG - {}".format(svg_count, dir_output),
                                            level=Qgis.Success, duration=5)


def replace_parameter(old_tag, dict_param_key, dict_param_value, path_tag):
    """Replaces in the svg file the parts needed to make the symbols editable in QGIS.

    :param old_tag: old part in path tag needed to modify
    :type old_tag: str, QString

    :param dict_param_key: key value of the tag
    :type dict_param_key: str, QString

    :param dict_param_value: value that replace the old tag
    :type dict_param_value: str, QString

    :param path_tag: all path tag that will be modify
    :type path_tag: str, QString

    :returns: path_tag without modification if an avoid parameter is detected or the new_path_tag after modifying him
    :rtype:  str, QString
    """

    # List of parameter to avoid for the change
    list_avoid_param = ["param(fill)",
                        "param(fill-opacity)",
                        "param(outline)",
                        "param(outline-opacity)",
                        "param(outline-width)",
                        "none"]

    # Verify if the value isn't in "list_avoid_param"
    if any([avoid in old_tag for avoid in list_avoid_param]):
        # If the value is "list_avoid_param", we don't change the value
        return path_tag
    else:
        # SVG file have different shape. We check to case :
        # "<path fill = '#000' ..." or "<path style = 'fill : #000 ...'"

        # First case, only the parameter value is between " or ' : <path fill = "#000" stroke = "1" ...
        idx_no_style_tag_dquote = old_tag.find("{}\"".format(dict_param_key))
        idx_no_style_tag_squote = old_tag.find("{}'".format(dict_param_key))

        if idx_no_style_tag_dquote != -1:
            # Add the new parameter between double quote
            idx_start_quote = idx_no_style_tag_dquote + len(dict_param_key) + 1
            idx_end_quote = old_tag.find('"', idx_start_quote)
            old_dquote_value = old_tag[idx_no_style_tag_dquote:idx_end_quote + 1]
            idx_dquote_value = old_dquote_value.find('"')
            dquote_value = old_dquote_value[idx_dquote_value + 1:]
            new_dquote_value = old_dquote_value.replace(dquote_value, dict_param_value + dquote_value)

            # Replace the old value by the new one define in "dict_param"
            new_tag = old_tag.replace(old_dquote_value, new_dquote_value)
            new_path_tag = path_tag.replace(old_tag, new_tag)

        elif idx_no_style_tag_squote != -1:
            # Add the new parameter between double quote
            idx_start_quote = idx_no_style_tag_squote + len(dict_param_key) + 1
            idx_end_quote = old_tag.find("'", idx_start_quote)
            old_squote_value = old_tag[idx_no_style_tag_squote:idx_end_quote + 1]
            idx_squote_value = old_squote_value.find("'")
            squote_value = old_squote_value[idx_squote_value + 1:]
            new_squote_value = old_squote_value.replace(squote_value, dict_param_value + squote_value)

            # Replace the old value by the new one define in "dict_param"
            new_tag = old_tag.replace(old_squote_value, new_squote_value)
            new_path_tag = path_tag.replace(old_tag, new_tag)

        else:
            # Second case, parameter and parameter value are between quote : <path style = "fill : #000 ; stroke : 1..."
            # Replace the old value by the new one define in "dict_param"
            new_tag = old_tag.replace(dict_param_key, dict_param_key + dict_param_value)
            new_path_tag = path_tag.replace(old_tag, new_tag)

        return new_path_tag
