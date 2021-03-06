#!/usr/bin/python
# -*- coding: utf-8 -*-

#######################################################################
###                                           Diálogo de definición de cristalizadores, UI_crystallizer                                      ###
#######################################################################

from PyQt4 import QtCore, QtGui

from equipment.liquid_solid import Crystallizer
from UI import UI_corriente
from equipment import parents
from lib import unidades
from tools import costIndex
from UI.widgets import Entrada_con_unidades


class UI_equipment(parents.UI_equip):
    """Diálogo de definición de cristalizadores"""
    def __init__(self, entrada=None, parent=None):
        """entrada: Parametro opcional de clase corriente que indica la corriente de entrada en el equipo"""
        super(UI_equipment, self).__init__(Crystallizer, entrada=False, parent=parent)
        self.entrada=entrada

        #Pestaña entrada
        self.Entrada= UI_corriente.Ui_corriente(entrada)
        self.Entrada.Changed.connect(self.cambiar_entrada)
        self.tabWidget.insertTab(0, self.Entrada,QtGui.QApplication.translate("equipment", "Entrada", None, QtGui.QApplication.UnicodeUTF8))

        #Pestaña calculo
        gridLayout_Calculo = QtGui.QGridLayout(self.tabCalculo)

        #Pestaña costos
        gridLayout_Costos = QtGui.QGridLayout(self.tabCostos)
        gridLayout_Costos.addWidget(QtGui.QLabel(QtGui.QApplication.translate("equipment", "Tipo:", None, QtGui.QApplication.UnicodeUTF8)), 1, 1)
        self.tipo=QtGui.QComboBox()
        self.tipo.addItem(QtGui.QApplication.translate("equipment", "Recirculación externa forzada", None, QtGui.QApplication.UnicodeUTF8))
        self.tipo.addItem(QtGui.QApplication.translate("equipment", "Internos de tubo forzado", None, QtGui.QApplication.UnicodeUTF8))
        self.tipo.addItem(QtGui.QApplication.translate("equipment", "Discontinuos a vacío", None, QtGui.QApplication.UnicodeUTF8))
        self.tipo.currentIndexChanged.connect(self.mostrarSubclasificacion)
        self.tipo.currentIndexChanged.connect(self.calcularCostos)
        gridLayout_Costos.addWidget(self.tipo, 1, 2, 1, 3)
        gridLayout_Costos.addWidget(QtGui.QLabel(QtGui.QApplication.translate("equipment", "Material:", None, QtGui.QApplication.UnicodeUTF8)), 2, 1)
        self.materialvacio=QtGui.QComboBox()
        self.materialvacio.addItem(QtGui.QApplication.translate("equipment", "Acero dulce", None, QtGui.QApplication.UnicodeUTF8))
        self.materialvacio.addItem(QtGui.QApplication.translate("equipment", "Acero recubierto de caucho", None, QtGui.QApplication.UnicodeUTF8))
        self.materialvacio.addItem(QtGui.QApplication.translate("equipment", "Acero inoxidable 304", None, QtGui.QApplication.UnicodeUTF8))
        self.materialvacio.currentIndexChanged.connect(self.calcularCostos)
        gridLayout_Costos.addWidget(self.materialvacio, 2, 2, 1, 3)
        self.materialotros=QtGui.QComboBox()
        self.materialotros.addItem(QtGui.QApplication.translate("equipment", "Acero dulce", None, QtGui.QApplication.UnicodeUTF8))
        self.materialotros.addItem(QtGui.QApplication.translate("equipment", "Acero inoxidable 304", None, QtGui.QApplication.UnicodeUTF8))
        self.materialotros.currentIndexChanged.connect(self.calcularCostos)
        gridLayout_Costos.addWidget(self.materialotros, 2, 2, 1, 3)
        gridLayout_Costos.addWidget(QtGui.QLabel(QtGui.QApplication.translate("equipment", "Volumen:", None, QtGui.QApplication.UnicodeUTF8)), 4, 4)
        self.Volumen=Entrada_con_unidades(unidades.Volume, "VolLiq", width=80)
        gridLayout_Costos.addWidget(self.Volumen,4,5,1,1)
        gridLayout_Costos.addItem(QtGui.QSpacerItem(10,10,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed),3,0,1,6)
        self.label4=QtGui.QLabel()
        self.label4.setText(QtGui.QApplication.translate("equipment", "Caudal calculado:", None, QtGui.QApplication.UnicodeUTF8))
        gridLayout_Costos.addWidget(self.label4, 4, 1, 1, 1)
        self.caudalcalculado=Entrada_con_unidades(unidades.MassFlow, readOnly=True, retornar=False)
        gridLayout_Costos.addWidget(self.caudalcalculado,4,2,1,1)
        gridLayout_Costos.addWidget(QtGui.QLabel(QtGui.QApplication.translate("equipment", "Caudal de diseño:", None, QtGui.QApplication.UnicodeUTF8)), 5, 1)
        self.caudaldiseno=Entrada_con_unidades(unidades.MassFlow)
        gridLayout_Costos.addWidget(self.caudaldiseno,5,2,1,1)
        gridLayout_Costos.addItem(QtGui.QSpacerItem(10,10,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed),6,0,1,6)

        self.Costos=costIndex.CostData(1.9, 2)
        self.Costos.valueChanged.connect(self.calcularCostos)
        gridLayout_Costos.addWidget(self.Costos,7,1,2,5)

        gridLayout_Costos.addItem(QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding),11,0,1,6)
        gridLayout_Costos.addItem(QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding),9,0,1,6)
        self.groupBox_Costos = QtGui.QGroupBox(QtGui.QApplication.translate("equipment", "Costos calculados", None, QtGui.QApplication.UnicodeUTF8))
        gridLayout_Costos.addWidget(self.groupBox_Costos,10,1,1,5)
        gridLayout_5 = QtGui.QGridLayout(self.groupBox_Costos)
        gridLayout_5.addWidget(QtGui.QLabel(QtGui.QApplication.translate("equipment", "Coste Adquisición:", None, QtGui.QApplication.UnicodeUTF8)),0,1,1,1)
        self.C_adq=Entrada_con_unidades(unidades.Currency, retornar=False, readOnly=True)
        gridLayout_5.addWidget(self.C_adq,0,2,1,1)
        gridLayout_5.addWidget(QtGui.QLabel(QtGui.QApplication.translate("equipment", "Coste Instalación:", None, QtGui.QApplication.UnicodeUTF8)),1,1,1,1)
        self.C_inst=Entrada_con_unidades(unidades.Currency, retornar=False, readOnly=True)
        gridLayout_5.addWidget(self.C_inst,1,2,1,1)

        self.tabWidget.setCurrentIndex(0)
        self.mostrarSubclasificacion(0)


    def mostrarSubclasificacion(self, ind):
        if ind<2:
            self.materialvacio.setVisible(False)
            self.materialotros.setVisible(True)
            self.Volumen.setReadOnly(True)
        else:
            self.materialvacio.setVisible(True)
            self.materialotros.setVisible(False)
            self.Volumen.setReadOnly(False)

    def cambiar_entrada(self, corriente):
        selfentrada=corriente
        self.calculo()

    def calculo(self):
        if self.todos_datos():

            self.rellenoSalida()

    def rellenoSalida(self):
        pass

    def todos_datos(self):
        pass

    def calcularCostos(self):
        if self.todos_datos():
            if self.tipo.currentIndex()==0:
                self.FireHeater.Coste(self.factorInstalacion.value(), 0, self.tipobox.currentIndex(), self.material.currentIndex())
            else:
                self.FireHeater.Coste(self.factorInstalacion.value(), 1, self.tipocilindrico.currentIndex(), self.material.currentIndex())
            self.C_adq.setValue(self.FireHeater.C_adq.config())
            self.C_inst.setValue(self.FireHeater.C_inst.config())

    def on_costIndex_clicked(self):
        dialog = costIndex.Ui_CostIndex()
        if dialog.exec_():
            self.indiceActual.setText(dialog.equipos.text())
            self.calcularCostos()


if __name__ == "__main__":
    import sys
    from lib.corriente import Corriente, Mezcla, Solid
    app = QtGui.QApplication(sys.argv)
    agua=Corriente(300, 1, 3600, Mezcla([62], [1]))
    dialogo = UI_equipment(agua)
    dialogo.show()
    sys.exit(app.exec_())
