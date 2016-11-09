# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from qgis.core import *
from ui_mergeLayers_dialog import Ui_mergeLayersDialogBase
import os, utils


# noinspection PyUnresolvedReferences
class mergeLayersDialog(QtGui.QDialog):

    def __init__(self, iface,  parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.parent = parent
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QtCore.QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', 'mergeLayers_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QtCore.QTranslator()
            self.translator.load(locale_path)
            QtCore.QCoreApplication.installTranslator(self.translator)

        self.NOMATCH  = "<no match>"

        self.ui = Ui_mergeLayersDialogBase()
        self.ui.setupUi(self)
        self.layers = []
        self.iface = iface
        self.updateLayers()
        self._initGui()

    def tr(self, message, **kwargs):
        trans = QtCore.QCoreApplication.translate('mergeLayers', message)
        if isinstance( trans, str ): return trans
        else: return message

    def _initGui(self):
        self.ui.matchTbl.setColumnWidth(0, 120)
        self.ui.matchTbl.setColumnWidth(1, 120)

        #ADD EVENTS
        self.iface.mapCanvas().layersChanged.connect( self.updateLayers )
        self.ui.sourceCbx.currentIndexChanged.connect( self.updateMatchWidget )
        self.ui.targetCbx.currentIndexChanged.connect( self.updateMatchWidget )
        self.ui.outputFileBtn.clicked.connect(self.setOutput)
        self.accepted.connect(self.executeMerge)

    def updateMatchWidget(self):
        sourceLyrName = self.ui.sourceCbx.currentText()
        targetLyrName = self.ui.targetCbx.currentText()
        sourceLyr = None
        targetLyr = None
        self.ui.matchTbl.setHorizontalHeaderLabels([sourceLyrName,targetLyrName])

        for lyr in self.layers:
            if lyr.name() == sourceLyrName:
                sourceLyr = lyr
            if lyr.name() == targetLyrName:
                targetLyr = lyr

        if not sourceLyr or not targetLyr:
            return

        sourceFields = sourceLyr.pendingFields()
        self.ui.matchTbl.setRowCount( sourceFields.count() )
        rowIndex = 0
        for field in sourceFields:
            sourceName = field.name()
            sourceType = field.type()
            targetFields = [self.NOMATCH] + [f.name() for f in targetLyr.pendingFields()
                                                      if f.type() == sourceType ]
            targetFieldCbx = QtGui.QComboBox()
            targetFieldCbx.insertItems(0, targetFields)

            if sourceName in targetFields:
                targetFieldCbx.setCurrentIndex( targetFields.index(sourceName) )

            #populate the table
            self.ui.matchTbl.setCellWidget( rowIndex, 0, QtGui.QLabel(sourceName) )
            self.ui.matchTbl.setCellWidget( rowIndex, 1, targetFieldCbx )
            rowIndex += 1

    def updateLayers(self):
        self.layers = QgsMapLayerRegistry.instance().mapLayers().values()
        lyrs = [layer.name() for layer in self.layers if layer.type() == QgsMapLayer.VectorLayer ]
        editLayers = [layer.name() for layer in self.layers
                      if layer.type() == QgsMapLayer.VectorLayer and layer.dataProvider().capabilities() ]
        self.ui.sourceCbx.clear()
        self.ui.targetCbx.clear()
        self.ui.sourceCbx.addItems( lyrs )
        self.ui.targetCbx.addItems( editLayers )

        self.updateMatchWidget()

    def table2fieldMap(self):
        fieldMap = []

        for n in range( self.ui.matchTbl.rowCount() ):
            sourceField = self.ui.matchTbl.cellWidget(n, 0).text()
            targetField = self.ui.matchTbl.cellWidget(n, 1).currentText()
            fieldMap.append(( targetField, sourceField ))
        return fieldMap

    def executeMerge(self):
        sourceLyr = None
        targetLyr = None
        for lyr in self.layers:
            if lyr.name() ==  self.ui.sourceCbx.currentText():
                sourceLyr = lyr
            if lyr.name() ==  self.ui.targetCbx.currentText():
                targetLyr = lyr

        if not sourceLyr or not targetLyr:
            QtGui.QMessageBox.warning(self.iface.mainWindow(), self.tr("Warning"),
                                      self.tr("Layers are not set correctly"), '')
            return

        if  sourceLyr == targetLyr:
            QtGui.QMessageBox.warning(self.iface.mainWindow(), self.tr("Warning"),
                                      self.tr("Target and source are the same."), '')
            return

        if self.ui.add2targetRadio.isChecked() and not (targetLyr.dataProvider().capabilities() & QgsVectorDataProvider.AddFeatures):
            QtGui.QMessageBox.warning(self.iface.mainWindow(), self.tr("Warning"),
                                      self.tr("Target is not editable, try merge to new layer"), '')
            return

        if sourceLyr.geometryType() != targetLyr.geometryType():
            QtGui.QMessageBox.warning(self.iface.mainWindow(), self.tr("Geometries don't match"),
                                      self.tr(
                                          "The geometries of inputlayer and targerlayer don't match, so the files can't be merged"), '')
            return

        if self.ui.merge2newRadio.isChecked() and len( self.ui.outputFileTxt.text() ) == 0:
            QtGui.QMessageBox.warning(self.iface.mainWindow(), self.tr("Need a output location"),
                                      self.tr(
                                          "Define a output location on for the merged layer by clicking on the 'File'-button"), '')
            return


        if self.ui.add2targetRadio.isChecked():
            self.addsource2target(sourceLyr, targetLyr)
        else:
            self.mergeSourceAndTarget(sourceLyr, targetLyr)

        self.refresh(targetLyr)

    def addsource2target(self, sourceLyr, targetLyr):
        newFeats = []
        fieldMap = self.table2fieldMap()
        targetType = targetLyr.dataProvider().storageType()

        targetLyr.beginEditCommand("Starting to append..")  # use editbuffer
        for sourceFeat in sourceLyr.getFeatures():
            newFeat = QgsFeature(targetLyr.pendingFields())

            for targetField, sourceField in fieldMap:
                if targetType == "ESRI Shapefile":
                    targetField = utils.nameMaxLenght( targetField , 10)

                if targetField != self.NOMATCH:
                    newFeat.setAttribute(targetField, sourceFeat[sourceField])

            newFeat.setGeometry(sourceFeat.geometry())
            newFeats.append(newFeat)

            if len(newFeats) > 5000:  # append in blocks of 5000 the speed up.
                targetLyr.dataProvider().addFeatures(newFeats)
                newFeats = []
        targetLyr.dataProvider().addFeatures(newFeats)  # add remaining
        targetLyr.endEditCommand()

    def mergeSourceAndTarget(self, source, target):
        fpath = self.ui.outputFileTxt.text()
        newlayer = utils.copyLayer(fpath, target)
        QgsMapLayerRegistry.instance().addMapLayer( newlayer )
        self.addsource2target(source, newlayer)

    def setOutput(self):
        home = os.path.expanduser('~')
        title = self.tr(u"Save As")
        ftypeFilter = "Shapefile (*.shp);;Geopackage (*.gpkg);;GeoJSON (*.geojson);;Mapinfo (*.tab);;GML ($.gml);;SQLITE (*.sqlite)"
        outFile = QtGui.QFileDialog.getSaveFileName( self, title, filter=ftypeFilter, directory=home )
        self.ui.outputFileTxt.setText(outFile)

    def refresh(self, layer=None):
        if self.iface.mapCanvas().isCachingEnabled() and isinstance(layer, QgsVectorLayer):
            layer.setCacheImage(None)
        else:
            self.iface.mapCanvas().refresh()
