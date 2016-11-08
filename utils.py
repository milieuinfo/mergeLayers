import os
from qgis.core import QgsVectorFileWriter, QgsFields, QgsCoordinateReferenceSystem, QGis, QgsVectorLayer

def copyLayer( path, layer ):
    "returns the new layer"
    flType = _getFtype(path)

    if flType == "ESRI Shapefile":
        if os.path.exists(path): QgsVectorFileWriter.deleteShapeFile( path )
        error = QgsVectorFileWriter.writeAsVectorFormat(layer, path, "CP1250", None, flType)
    else:
        if os.path.exists(path): os.remove(path)
        error = QgsVectorFileWriter.writeAsVectorFormat(layer, path, "utf-8", None, flType)

    if error == QgsVectorFileWriter.NoError:
        layer_name = os.path.splitext( os.path.basename( path ))[0]
        newlayer = QgsVectorLayer(path, layer_name, "ogr")

        if newlayer.isValid(): return newlayer
        else: raise Exception("Could not read output")
    else:
        raise Exception("Could not write output")

def nameMaxLenght( fieldName , maxLen=10):
    if len( fieldName ) > maxLen:
        return fieldName[:maxLen]
    else:
        return fieldName

def _getFtype(path):
    ext = os.path.splitext(path)[1]
    if "SHP" == ext.upper():
        flType = "ESRI Shapefile"
    elif "SQLITE" == ext.upper():
        flType = "SQLite"
    elif "GPKG" == ext.upper():
        flType = "GPKG"
    elif "GML" == ext.upper():
        flType = "GML"
    elif 'TAB' == ext.upper():
        flType = 'MapInfo File'
    elif 'JSON' in ext.upper():
        flType = 'GeoJSON'
    else:
        flType = "ESRI Shapefile"
    return flType