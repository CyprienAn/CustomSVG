# Que fait ce plugin ?
Il permet l'adaptation de fichier SVG afin qu'ils soient modifiables dans QGIS.

# Comment ?
Il modifie tous les SVG d'un dossier en remplacant les paramètres `styles` contenu dans les balises `path` et en réenregistrant le nouveau SVG au format `qgs_oldname.svg`.
Les paramètres modifiés sont les suivants:
* fill : `param(fill)`,
* fill-opacity : `param(fill-opacity)`,
* stroke : `param(outline)`,
* stroke-opacity : `param(outline-opacity)`,
* stroke-width : `param(outline-width)`.

# Exemple
Avant modification :

    <path
        style="fill:none;stroke:#000000;stroke-width:0.4;"
    />
Après modification :

    <path
        style="fill:none;stroke:param(outline) #000000;stroke-width:param(outline-width) 0.4;"
    />