# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from qgis.core import *
from ui_mergeLayers_dialog import Ui_mergeLayersDialogBase
import os
class mergeLayersDialog(QtGui.QDialog):

    def __init__(self, iface,  parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QtCore.QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', 'mergeLayers_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QtCore.QTranslator()
            self.translator.load(locale_path)
            if QtCore.qVersion() > '4.3.3':
               QtCore.QCoreApplication.installTranslator(self.translator)
        self.NOMATCH  =  self.tr("<no match>")

        self.ui = Ui_mergeLayersDialogBase()
        self.ui.setupUi(self)
        self.layers = []
        self.iface = iface
        self.updateLayers()
        self._initGui()

    def tr(self, message):
        return QCoreApplication.translate('mergeLayers', message)

    def _initGui(self):
        self.ui.matchTbl.setColumnWidth(0, 120)
        self.ui.matchTbl.setColumnWidth(1, 120)

        #ADD EVENTS
        self.iface.mapCanvas().layersChanged.connect(self.updateLayers)
        self.ui.sourceCbx.currentIndexChanged.connect( self.updateMatchWidget )
        self.ui.targetCbx.currentIndexChanged.connect( self.updateMatchWidget )
        self.accepted.connect(self.executeMerge)

    def updateMatchWidget(self):
        sourceLyrName = self.ui.sourceCbx.currentText()
        targetLyrName = self.ui.targetCbx.currentText()
        sourceLyr = None
        targetLyr = None
        self.ui.matchTbl.setHorizontalHeaderLabels([sourceLyrName,targetLyrName])
        self.ui.infoLbl.setText( self.tr( "Layer {0} will be added to layer {1}" ).format(sourceLyrName,targetLyrName))

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
            targetFields = [self.NOMATCH] + [f.name() for f in targetLyr.pendingFields() if f.type() == sourceType]
            targetFieldCbx = QtGui.QComboBox()
            targetFieldCbx.insertItems(0, targetFields)
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
            return

        fieldMap = self.table2fieldMap()
        newFeats = []

        for sourceFeat in sourceLyr.getFeatures():
            newFeat = QgsFeature(targetLyr.pendingFields())

            for targetField, sourceField in fieldMap:
                if targetField != self.NOMATCH:
                    newFeat[targetField] = sourceFeat[sourceField]

            newFeat.setGeometry( sourceFeat.geometry() )
            newFeats.append(newFeat)

        targetLyr.dataProvider().addFeatures(newFeats)
        self.iface.mapCanvas().refresh()