#!/usr/bin/python
# -*- coding: utf-8 -*-

###Modulo que define los equipos de destilación

import os

from scipy import log, exp, pi, log10, linspace
from scipy.optimize import fsolve
from PyQt4.QtGui import QApplication

from lib import unidades
from lib.corriente import Corriente
from lib.plot import Plot
from parents import equipment
from heatExchanger import Heat_Exchanger


class Flash(equipment):
    """Clase que modela los tambores flash.

    Parámetros:
        entrada: instancia de la clase corriente que define la corriente de entrada en la bomba
        flash: método de cálculo
            0   -   Usar P y T de la entrada

    Coste:
        orientacion:
            0   -   Horizontal
            1   -   Vertical
        material:
            0   -   Carbon steel
            1   -   Stainless steel 304
            2   -   Stainless steel 316
            3   -   Carpenter 20CB-3
            4   -   Nickel 200
            5   -   Monel 400
            6   -   Inconel 600
            7   -   Incoloy 825
            8   -   Titanium
        densidad: densidad del material
        diametro: diametro recipiente
        longitud
        espesor: espesor de la cubierta
        cabeza: tipo de cabeza del recipiente
            0   -   Ellipsoidal
            1   -   Hemispherical
            2   -   Bumped
            3   -   Flat
        espesor_cabeza: espesor de la cubierta en la cabeza
        reborde: longitud reborde
    """
    title=QApplication.translate("pychemqt", "Flash Separator")
    help=""
    kwargs={"entrada": None,
                    "flash": 0,

                    "f_install": 1.7,
                    "Base_index": 0.0,
                    "Current_index": 0.0,
                    "orientacion": 0,
                    "material": 0,
                    "densidad": 0.0,
                    "diametro": 0.0,
                    "longitud": 0.0,
                    "espesor": 0.0,
                    "cabeza": 0,
                    "espesor_cabeza": 0.0,
                    "reborde": 0.0}

    kwargsInput=("entrada", )
    kwargsList=("flash", "orientacion", "material", "cabeza")
    kwargsValue=("diametro", "longitud", "espesor", "espesor_cabeza", "reborde")
    calculateCostos=("C_adq", "C_inst", "Peso", "Volumen")
    indiceCostos=3

    TEXT_FLASH=[QApplication.translate("pychemqt", "Use P and T from input stream")]
    TEXT_ORIENTATION=[QApplication.translate("pychemqt", "Horizontal"),
                            QApplication.translate("pychemqt", "Vertical")]
    TEXT_MATERIAL=[QApplication.translate("pychemqt", "Carbon steel"),
                                QApplication.translate("pychemqt", "Stainless steel 304"),
                                QApplication.translate("pychemqt", "Stainless steel 316"),
                                QApplication.translate("pychemqt", "Carpenter 20CB-3"),
                                QApplication.translate("pychemqt", "Nickel 200"),
                                QApplication.translate("pychemqt", "Monel 400"),
                                QApplication.translate("pychemqt", "Inconel 600"),
                                QApplication.translate("pychemqt", "Incoloy 825"),
                                QApplication.translate("pychemqt", "Titanium")]
    TEXT_HEAD=[QApplication.translate("pychemqt", "Ellipsoidal"),
                                QApplication.translate("pychemqt", "Hemispherical"),
                                QApplication.translate("pychemqt", "Bumped"),
                                QApplication.translate("pychemqt", "Flat")]


    @property
    def isCalculable(self):
        if self.kwargs["f_install"] and self.kwargs["Base_index"] and self.kwargs["Current_index"] and self.kwargs["diametro"] and self.kwargs["longitud"] and self.kwargs["espesor"] :
            self.statusCoste=True
        else:
            self.statusCoste=False

        if not self.kwargs["entrada"]:
            self.msg=QApplication.translate("pychemqt", "undefined input")
            self.status=0
            return

        self.msg=""
        self.status=1
        return True


    def calculo(self):
        self.entrada=self.kwargs["entrada"]
        if self.kwargs["flash"]==0:
            Vapor=self.entrada.clone(mezcla=self.entrada.Gas)
            Liquido=self.entrada.clone(mezcla=self.entrada.Liquido)
            self.salida=[Vapor, Liquido]
        self.Tout=Vapor.T
        self.Pout=Vapor.P
        self.VaporMolarFlow=Vapor.caudalmolar
        self.VaporMassFlow=Vapor.caudalmasico
        self.VaporVolFlow=Vapor.Q
        self.VaporMolarComposition=Vapor.fraccion
        self.VaporMassComposition=Vapor.fraccion_masica
        self.LiquidMolarFlow=Liquido.caudalmolar
        self.LiquidMassFlow=Liquido.caudalmasico
        self.LiquidVolFlow=Liquido.Q
        self.LiquidMolarComposition=Liquido.fraccion
        self.LiquidMassComposition=Liquido.fraccion_masica

    def volumen(self):
        self.Di=unidades.Length(0)
        self.L=unidades.Length(0)
        self.reborde=0
        self.espesor=0
        self.espesor_cabeza=0

        V_carcasa=pi/4*self.Di**2*self.L

        if self.kwargs["cabeza"]==0:
            V_cabeza=4./3*pi/8*self.Di**3
        elif self.kwargs["cabeza"]==1:
            V_cabeza=4./3*pi/8/2*self.Di**3
        elif self.kwargs["cabeza"]==2:
            V_cabeza=0.215483/2*self.Di**3
        else:
            V_cabeza=0.

        self.V=unidades.Volume(V_carcasa+V_cabeza)


    def peso(self):
        W_carcasa=pi/4*(self.De**2-self.Di**2)*self.L*self.densidad

        if self.kwargs["cabeza"]==3:
            W_cabeza=pi/4*self.Di**2*self.espesor_cabeza*self.densidad
        else:
            ratio=self.De/self.espesor_cabeza
            if self.kwargs["cabeza"]==0:
                if ratio>20:
                    hb=1.24
                else:
                    hb=1.3
            elif self.kwargs["cabeza"]==2:
                if ratio>50:
                    hb=1.09
                elif ratio>30:
                    hb=1.11
                else:
                    hb=1.15
            else:
                if ratio>30:
                    hb=1.6
                elif ratio>18:
                    hb=1.65
                else:
                    hb=1.70
            Do=hb*self.De+2*self.reborde
            W_cabeza=pi/4*Do**2*self.espesor_cabeza*self.densidad

        self.W=unidades.Mass(W_carcasa+2*W_cabeza)


    def coste(self):
        if self.kwargs["densidad"]:
            self.densidad=unidades.Density(self.kwargs["densidad"])
        else:
            self.densidad=unidades.Density(501, "lbft3") #La densidad del acero inoxidable 304
        self.Di=unidades.Length(self.kwargs["diametro"])
        self.L=unidades.Length(self.kwargs["longitud"])
        self.espesor=unidades.Length(self.kwargs["espesor"])
        espesor_cabeza=self.kwargs["espesor_cabeza"]
        if self.kwargs["espesor_cabeza"]:
            self.espesor_cabeza=unidades.Length(self.kwargs["espesor_cabeza"])
        else:
            self.espesor_cabeza=self.espesor
        self.reborde=unidades.Length(self.kwargs["reborde"])
        self.De=unidades.Length(self.Di+2*espesor)

        self.volumen()
        self.peso()

        Fm=[1., 1.7, 2.1, 3.2, 5.4, 3.6, 3.9, 3.7, 7.7][self.kwargs["material"]]

        if self.kwargs["tipo"]==0:
            Cb=exp(8.571-0.233*log(self.W.lb)+0.04333*log(self.W.lb)**2)
            Ca=1370*self.Di.ft**0.2029
        else:
            Cb=exp(9.1-0.2889*log(self.W.lb)+0.04576*log(self.W.lb)**2)
            Ca=246*self.Di.ft**0.7396*self.L.ft**0.7068

        C=Fm*Cb+Ca

        self.C_adq=unidades.Currency(C * self.kwargs["Current_index"] / self.kwargs["Base_index"])
        self.C_inst=unidades.Currency(self.C_adq*self.kwargs["f_install"])


    def propTxt(self):
        txt="#---------------"+QApplication.translate("pychemqt", "Calculate properties")+"-----------------#"+os.linesep
        txt+="%-25s\t %s" %(QApplication.translate("pychemqt", "Mode"), self.TEXT_FLASH[self.kwargs["flash"]])+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Output Temperature"), self.salida[0].T.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Output Pressure"), self.salida[0].P.str)+os.linesep
        txt+=os.linesep+"#"+QApplication.translate("pychemqt", "Vapor Output Molar Composition")+os.linesep
        for componente, fraccion in zip(self.salida[0].componente, self.salida[0].fraccion):
            txt+="%-25s\t %0.4f" %(componente.nombre, fraccion)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Vapor Output Mass Flow"), self.salida[0].caudalmolar.str)+os.linesep
        txt+=os.linesep+"#"+QApplication.translate("pychemqt", "Liquid Output Molar Composition")+os.linesep
        for componente, fraccion in zip(self.salida[1].componente, self.salida[1].fraccion):
            txt+="%-25s\t %0.4f" %(componente.nombre, fraccion)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Liquid Output Mass Flow"), self.salida[1].caudalmolar.str)+os.linesep
        return txt

    @classmethod
    def propertiesEquipment(cls):
        list=[(QApplication.translate("pychemqt", "Mode"), ("TEXT_FLASH", "flash"), str),
                (QApplication.translate("pychemqt", "Output Temperature"), "Tout", unidades.Temperature),
                (QApplication.translate("pychemqt", "Output Pressure"), "Pout", unidades.Pressure),
                (QApplication.translate("pychemqt", "Vapor Output Molar Flow"), "VaporMolarFlow", unidades.MolarFlow),
                (QApplication.translate("pychemqt", "Vapor Output Mass Flow"), "VaporMassFlow", unidades.MassFlow),
                (QApplication.translate("pychemqt", "Vapor Output Volumetric Flow"), "VaporVolFlow", unidades.VolFlow),
                (QApplication.translate("pychemqt", "Vapor Output Molar Composition"), "VaporMolarComposition", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Vapor Output Mass Composition"), "VaporMassComposition", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Liquid Output Molar Flow"), "LiquidMolarFlow", unidades.MolarFlow),
                (QApplication.translate("pychemqt", "Liquid Output Mass Flow"), "LiquidMassFlow", unidades.MassFlow),
                (QApplication.translate("pychemqt", "Liquid Output Volumetric Flow"), "LiquidVolFlow", unidades.VolFlow),
                (QApplication.translate("pychemqt", "Liquid Output Molar Composition"), "LiquidMolarComposition", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Liquid Output Mass Composition"), "LiquidMassComposition", unidades.Dimensionless),
                ]
        return list

    def propertiesListTitle(self, index):
        """Define los titulos para los popup de listas"""
        lista=[comp.nombre for comp in self.kwargs["entrada"].componente]
        return lista


class Tower(equipment):
    """Clase general que define las propiedades comunes de las unidades de destilación"""
    title="Torre de destilación"
    help=""

    Condenser=Heat_Exchanger()
    Reboiler=Heat_Exchanger()

    calculateCostos=("C_pisos", "C_carcasa", "C_accesorios", "C_col_adq", "C_adq", "C_inst")

    TEXT_PROCESS=[QApplication.translate("pychemqt", "Destillation"),
                                QApplication.translate("pychemqt", "Absortion")]
    TEXT_COLUMN=[QApplication.translate("pychemqt", "Tray column"),
                                QApplication.translate("pychemqt", "Packed column")]
    TEXT_MATERIAL=[QApplication.translate("pychemqt", "Carbon steel"),
                                QApplication.translate("pychemqt", "Stainless steel 304"),
                                QApplication.translate("pychemqt", "Stainless steel 316"),
                                QApplication.translate("pychemqt", "Carpenter 20CB-3"),
                                QApplication.translate("pychemqt", "Nickel 200"),
                                QApplication.translate("pychemqt", "Monel 400"),
                                QApplication.translate("pychemqt", "Inconel 600"),
                                QApplication.translate("pychemqt", "Incoloy 825"),
                                QApplication.translate("pychemqt", "Titanium")]
    TEXT_TRAY=[QApplication.translate("pychemqt", "Valve tray"),
                        QApplication.translate("pychemqt", "Grid tray"),
                        QApplication.translate("pychemqt", "Bubble cap tray"),
                        QApplication.translate("pychemqt", "Sieve tray")]

    def isCalculable(self):
        if self.kwargs["tipo"]:
            if not self.kwargs["C_unitario"]:
                self.statusCoste=False
                return

        if self.kwargs["Di"] and self.kwargs["h"] and self.kwargs["W"] and self.kwargs["Wb"]:
            self.statusCoste=True
        else:
            self.statusCoste=False


    def peso(self):
        """Cálculo del peso de la carcasa"""
        return unidades.Mass(pi*self.kwargs["Di"]*(self.kwargs["h"]+0.8116*self.kwargs["Di"])*0.5*(self.kwargs["Wb"]+self.kwargs["W"])*self.densidad)

    def volumen(self):
        """Cálculo del volumen interno de la columna, útil ya que corresponde al volumen de relleno necesario en columnas de relleno"""
        return unidades.Volume(pi/4*self.kwargs["Di"]**2*self.kwargs["h"])


    def McCabe(self, LK=0, HK=1):
        A = self.kwargs["entrada"].componente[LK].nombre
        B = self.kwargs["entrada"].componente[HK].nombre
        P = self.kwargs["entrada"].P
        Psat = dict()
        Psat[A] = self.kwargs["entrada"].componente[LK].Pv
        Psat[B] = self.kwargs["entrada"].componente[HK].Pv
        Tsat = dict()
        for i, s in enumerate(Psat.keys()):
            Tsat[s] = lambda P, s=s: fsolve(lambda T: Psat[s](T)-P,self.kwargs["entrada"].componente[i].Tb)[0]

        T = linspace(Tsat[A](P),Tsat[B](P))

        x = lambda T: (P-Psat[B](T))/(Psat[A](T)-Psat[B](T))
        y = lambda T: x(T)*Psat[A](T)/P

        xB = 1-self.kwargs["HKsplit"]
        xF = self.kwargs["entrada"].fraccion[LK]
        xD = self.kwargs["LKsplit"]
        Tbub = fsolve(lambda T:x(T) - xF,T[25])
        yF = y(Tbub)

        if self.kwargs["R"]:
            R=self.kwargs["R"]
        else:
            Eslope = (xD-yF)/(xD-xF)
            Rmin = Eslope/(1-Eslope)
            R=self.kwargs["R_Rmin"]*Rmin

        zF = xD-R*(xD-xF)/(R+1)
        Sslope = (zF-xB)/(xF-xB)
        S = 1/(Sslope-1)
        xP = xD
        yP = xD

        dialog=Plot()
        dialog.plot.ax.grid(True)
        dialog.plot.ax.set_title(QApplication.translate("pychemqt", "x-y Diagram for") + "{:s}/{:s} P={:s}".format(A,B,P.str), size="x-large")
        dialog.plot.ax.set_xlabel(QApplication.translate("pychemqt", "Liquid Mole Fraction")+" {:s}".format(A), size="x-large")
        dialog.plot.ax.set_ylabel(QApplication.translate("pychemqt", "Vapor Mole Fraction")+" {:s}".format(B), size="x-large")
        dialog.plot.ax.set_xticks(linspace(0,1.0,21))
        dialog.plot.ax.set_yticks(linspace(0.05,1.0,20))
        dialog.addData([0,1],[0,1],'b--')
        dialog.addData(map(x,T),map(y,T))
        dialog.addData([xB,xB],[0,xB],'r--')
        dialog.addData(xB,xB,'ro',ms=5)
        dialog.addText(xB+0.005,0.02,'xB = {:0.3f}'.format(float(xB)))
        dialog.addData([xF,xF,xF],[0,xF,yF],'r--')
        dialog.addData([xF,xF],[xF,yF],'ro',ms=5)
        dialog.addText(xF+0.005,0.02,'xF = {:0.3f}'.format(float(xF)))
        dialog.addData([xD,xD],[0,xD],'r--')
        dialog.addData(xD,xD,'ro',ms=5)
        dialog.addText(xD-0.005,0.02,'xD = {:0.3f}'.format(float(xD)), ha="right")

        dialog.addData([xD,xF],[xD,yF],'r--')
        dialog.addData([xD,xF],[xD,zF],'r-')
        dialog.addData([xB,xF],[xB,xB + (S+1)*(xF-xB)/S],'r-')

        nTray = 0
        while xP > xB:
            nTray += 1
            Tdew = fsolve(lambda T:y(T) - yP, T[25])
            xQ = xP
            xP = x(Tdew)
            dialog.addData([xQ,xP],[yP,yP],'r')
            dialog.addData(xP,yP,'ro',ms=5)
            dialog.addText(xP-0.03,yP,nTray)

            yQ = yP
            yP = min([xD - (R/(R+1))*(xD-xP),xB + ((S+1)/S)*(xP-xB)])
            dialog.addData([xP,xP],[yQ,yP],'r')

        nTray -= 1

        dialog.addText(0.1,0.90,'Rmin = {:0.2f}'.format(float(Rmin)), size="large")
        dialog.addText(0.1,0.85,'R = {:0.2f}'.format(float(R)), size="large")
        dialog.addText(0.1,0.80,'S = {:0.2f}'.format(float(S)), size="large")
        dialog.addText(0.1,0.75,'nTrays = {:d}'.format(int(nTray)), size="large")


        dialog.exec_()


    def coste(self):
        self.tipo_pisos=kwargs.get("tipo_pisos", 0)
        self.material_columna=kwargs.get("material_columna", 0)
        self.material_pisos=kwargs.get("material_pisos", 0)

        Di=unidades.Length(self.kwargs["Di"]).ft
        L=unidades.Length(self.kwargs["L"]).ft
        W=self.peso().lb

        f1=[1., 1.7, 2.1, 3.2, 5.4, 3.6, 3.9, 3.7, 7.7][self.kwargs["material_columna"]]
        if self.kwargs["proceso"]:
            #Destilación
            Cb=exp(7.123+0.1478*log(W)+0.02488*log(W)**2+0.0158*L/Di*log(self.kwargs["Wb"]/self.kwargs["W"]))
            Cp=204.9*Di**0.6332*L**0.8016
        else:
            #Absorción
            Cb=exp(6.629+0.1826*log(W)+0.02297*log(W)**2)
            Cp=246.4*Di**0.7396*L**0.7068

        if self.kwargs["tipo"]==0:
            #Columna de pisos
            f2=[1., 1.189+0.0577*Di, 1.401+0.0724*Di, 1.525+0.0788*Di, 1., 2.306+0.112*Di, 1., 1., 1.][self.kwargs["material_pisos"]]
            f3=[1., 0.8, 1.59, 0.85][self.kwargs["tipo_pisos"]]
            if self.NTray<=20:
                f4=2.25/1.0414**self.NTray
            else:
                f4=1.
            Ci=f2*f3*f4*self.NTray*375.8*exp(0.1739*Di)
        else:
            #Columna de relleno
            Ci=self.volumen()*self.kwargs["C_unitario"]

        C=f1*Cb+Cp+Ci

        C_adq=C*self.Current_index/self.Base_index
        C_inst=C_adq*self.f_install

        self.C_pisos=Ci #indica el coste de los pisos en las columnas de pisos y el coste del relleno en las torres de relleno
        self.C_carcasa=f1*Cb
        self.C_accesorios=Cp   #otros gastos, plataforma, escalera...

        self.C_col_adq=C_adq
        self.C_col_inst=C_inst

        self.C_adq=C_adq+self.caldera.C_adq+self.condensador.C_adq
        self.C_inst=C_inst+self.caldera.C_inst+self.condensador.C_inst


class ColumnFUG(Tower):
    """Columna de destilación sencilla que usa el método aproximado de Fenske-Underwood-Gilliland

    Parámetros:
        entrada: instancia de la clase corriente que define la corriente de entrada en la bomba
        feed: Método de cálculo del piso de la alimentación
            0   -   Kirkbride
            1   -   Fenske
        LK: Indice que indica el componente clave ligero
        LKsplit: Especificación del componente clave ligero
        HK: Indice que indica el componente clave pesado
        HKsplit: Especificación del componente clave pesado
        condenser: tipo de condensador
            0   -   Total
            1   -   Parcial
        R: razón de reflujo
        R_Rmin: razón de reflujo con respecto a la mínima
        Pd: Presión de diseño de la columna, si no se especifica se usa la presión de la entrada
        DeltaP: Caida de presión en la columna

    Coste:
        proceso: tipo de proceso
            0   -   Absorción
            1   -   Destilación
        tipo: tipo de columna
            0   -   Torre de pisos
            1   -   Torre de relleno
        tipo_pisos: tipo de pisos
            0   -   De válvula
            1   -   De rejilla
            2   -   De borboteo
            3   -   De tamiz
        material_columna
            0   -   carbon steel
            1   -   Stainless steel 304
            2   -   Stainless steel 316
            3   -   Carpenter 20CB-3
            4   -   Nickel 200
            5   -   Monel 400
            6   -   Inconel 600
            7   -   Incoloy 825
            8   -   Titanium
        material_pisos
            0   -   carbon steel
            1   -   Stainless steel 304
            2   -   Stainless steel 316
            3   -   Carpenter 20CB-3
            4   -   Nickel 200
            5   -   Monel 400
            6   -   Inconel 600
            7   -   Incoloy 825
            8   -   Titanium
        C_unitario: Parametro opcional, solo necesario en las columnas de relleno, coste unitario de relleno, $/m3
        Di: Diametro interno
        h: altura
        W: Espesor carcasa
        Wb: Espesor carcasa fondo
    """
    title=QApplication.translate("pychemqt", "Column (Shortcut method)")
    help=""
    kwargs={"entrada": None,
                    "feed": 0,
                    "LK": 0,
                    "LKsplit": 0.0,
                    "HK": 0,
                    "HKsplit": 0.0,
                    "condenser": 0,
                    "R": 0.0,
                    "R_Rmin": 0.0,
                    "Pd": 0.0,
                    "DeltaP": 0.0,

                    "f_install": 3,
                    "Base_index": 0.0,
                    "Current_index": 0.0,
                    "proceso": 0,
                    "tipo": 0,
                    "tipo_pisos": 0,
                    "material_columna": 0,
                    "material_pisos": 0,
                    "C_unitario": 0.0,
                    "Di": 0.0,
                    "h": 0.0,
                    "W": 0.0,
                    "Wb": 0.0
                    }
    kwargsInput=("entrada", )
    kwargsValue=("LKsplit", "HKsplit", "R", "R_Rmin", "Pd", "DeltaP")
    kwargsList=("feed", "LK", "HK", "condenser")
    calculateValue=("DutyCondenser", "DutyReboiler", "Rmin", "RCalculada", "Nmin", "NTray", "N_feed")
    indiceCostos=3

    TEXT_FEED=["Kirkbride", "Fenske"]
    TEXT_CONDENSER=[QApplication.translate("pychemqt", "Total"),
                                            QApplication.translate("pychemqt", "Partial")]


    def cleanOldValues(self, **kwargs):
        if kwargs.has_key("R"):
            self.kwargs["R_Rmin"]=0.0
        elif kwargs.has_key("R_Rmin"):
            self.kwargs["R_Rmin"]=0.0
        self.kwargs.update(kwargs)

    @property
    def isCalculable(self):
        Tower.isCalculable(self)

        self.statusMcCabe=True
        if not self.kwargs["R"] and not self.kwargs["R_Rmin"]:
            self.statusMcCabe=False
        elif not self.kwargs["LKsplit"] or not self.kwargs["HKsplit"]:
            self.statusMcCabe=False

        if not self.kwargs["entrada"]:
            self.msg=QApplication.translate("pychemqt", "undefined input")
            self.status=0
            return

        if not self.kwargs["R"] and not self.kwargs["R_Rmin"]:
            self.msg=QApplication.translate("pychemqt", "undefined reflux ratio condition")
            self.status=0
            return

        if not self.kwargs["LKsplit"]:
            self.msg=QApplication.translate("pychemqt", "undefined light key component recuperation in top product")
            self.status=0
            return
        if not self.kwargs["HKsplit"]:
            self.msg=QApplication.translate("pychemqt", "undefined heavy key component recuperation in bottom product")
            self.status=0
            return
        if self.kwargs["LK"]==-1:
            self.msg=QApplication.translate("pychemqt", "undefined light key component")
            self.status=0
            return
        if self.kwargs["HK"]==-1:
            self.msg=QApplication.translate("pychemqt", "undefined heavy key component")
            self.status=0
            return

        if self.kwargs["HK"]<=self.kwargs["LK"]:
            self.msg=QApplication.translate("pychemqt", "key component bad specified")
            self.status=0
            return

        self.msg=""
        self.status=1
        return True


    def calculo(self):
        self.entrada=self.kwargs["entrada"]
        self.LKsplit=unidades.Dimensionless(self.kwargs["LKsplit"])
        self.HKsplit=unidades.Dimensionless(self.kwargs["HKsplit"])
        self.RCalculada=unidades.Dimensionless(self.kwargs["R"])
        self.R_Rmin=unidades.Dimensionless(self.kwargs["R_Rmin"])
        if self.kwargs["Pd"]:
            self.Pd=unidades.Pressure(self.kwargs["Pd"])
        else:
            self.Pd=self.entrada.P
        self.DeltaP=unidades.Pressure(self.kwargs["DeltaP"])

        #Estimate splits of components
        b=[]
        d=[]
        for i, caudal_i in enumerate(self.entrada.caudalunitariomolar):
            if i==self.kwargs["LK"]:
                b.append(caudal_i*(1-self.LKsplit))
                d.append(caudal_i*self.LKsplit)
            elif i==self.kwargs["HK"]:
                d.append(caudal_i*(1-self.HKsplit))
                b.append(caudal_i*self.HKsplit)
            elif self.entrada.eos.Ki[i]>self.entrada.eos.Ki[self.kwargs["LK"]]:
                b.append(0)
                d.append(caudal_i)
            elif self.entrada.eos.Ki[i]<self.entrada.eos.Ki[self.kwargs["HK"]]:
                d.append(0)
                b.append(caudal_i)
            else:
                d.append(caudal_i*0.5)
                b.append(caudal_i*0.5)

        while True:
            bo=b
            do=d

            xt=[Q/sum(d) for Q in d]
            xb=[Q/sum(b) for Q in b]
            Qt=sum([di*comp.M for di, comp in zip(d, self.entrada.componente)])
            Qb=sum([bi*comp.M for bi, comp in zip(b, self.entrada.componente)])
            destilado=Corriente(T=self.entrada.T, P=self.Pd, caudalMasico=Qt, fraccionMolar=xt)
            residuo=Corriente(T=self.entrada.T, P=self.Pd, caudalMasico=Qb, fraccionMolar=xb)
            #TODO: Add algorithm to calculate Pd and condenser type fig 12.4 pag 230
            
            #Fenske equation for Nmin
            alfam=(destilado.eos.Ki[self.kwargs["LK"]]/destilado.eos.Ki[self.kwargs["HK"]]*residuo.eos.Ki[self.kwargs["LK"]]/residuo.eos.Ki[self.kwargs["HK"]])**0.5
            Nmin=log10(destilado.caudalunitariomolar[self.kwargs["LK"]]/destilado.caudalunitariomolar[self.kwargs["HK"]] * residuo.caudalunitariomolar[self.kwargs["HK"]]/residuo.caudalunitariomolar[self.kwargs["LK"]]) / log10(alfam)

            #Evaluación composición salidas
            b=[]
            d=[]
            for i in range(len(self.entrada.ids)):
                if i in [self.kwargs["LK"], self.kwargs["HK"]]:
                    b.append(bo[i])
                    d.append(do[i])
                else:
                    alfa=(destilado.eos.Ki[i]/destilado.eos.Ki[self.kwargs["HK"]]*residuo.eos.Ki[i]/residuo.eos.Ki[self.kwargs["HK"]])**0.5
                    b.append(self.entrada.caudalunitariomolar[i]/(1+do[self.kwargs["HK"]]/bo[self.kwargs["HK"]]*alfa**Nmin))
                    d.append(self.entrada.caudalunitariomolar[i]*do[self.kwargs["HK"]]/bo[self.kwargs["HK"]]*alfa**Nmin/(1+do[self.kwargs["HK"]]/bo[self.kwargs["HK"]]*alfa**Nmin))

            res=sum([abs(inicial-final) for inicial, final in zip(bo, b)]) + sum([abs(inicial-final) for inicial, final in zip(do, d)])
            if res<1e-10:
                self.Nmin=Nmin-self.kwargs["condenser"]+1
                break


        #Calculo de la razón de reflujo mínima, ecuación de Underwood
        alfa=self.entrada.eos.Ki[self.kwargs["LK"]]/self.entrada.eos.Ki[self.kwargs["HK"]]
        self.Rmin=unidades.Dimensionless(abs(float(destilado.caudalmolar/self.entrada.caudalmolar*(destilado.fraccion[self.kwargs["LK"]]/self.entrada.Liquido.fraccion[self.kwargs["LK"]]-alfa*destilado.fraccion[self.kwargs["HK"]]/self.entrada.Liquido.fraccion[self.kwargs["HK"]])/(alfa-1))))

        #Cálculo del número de etapas reales, ecuación de Gilliland
        if self.R_Rmin and not self.RCalculada:
            self.RCalculada=unidades.Dimensionless(self.R_Rmin*self.Rmin)
        X=(self.RCalculada-self.Rmin)/(self.RCalculada+1)
        Y=1-exp((1+54.4*X)/(11+117.2*X)*(X-1)/X**0.5)
        self.NTray=unidades.Dimensionless((Y+self.Nmin)/(1-Y)-1-self.kwargs["condenser"])

        #Cálculo del piso de la alimentación
        if self.kwargs["feed"]:       #Ec. de Fenske
            alfa_b=residuo.eos.Ki[self.kwargs["LK"]]/residuo.eos.Ki[self.kwargs["HK"]]
            alfa_d=destilado.eos.Ki[self.kwargs["LK"]]/destilado.eos.Ki[self.kwargs["HK"]]
            alfa_f=self.entrada.eos.Ki[self.kwargs["LK"]]/self.entrada.eos.Ki[self.kwargs["HK"]]
            ratio=log(destilado.fraccion[self.kwargs["LK"]]/self.entrada.fraccion[self.kwargs["LK"]]*self.entrada.fraccion[self.kwargs["HK"]]/destilado.fraccion[self.kwargs["HK"]])/log(self.entrada.fraccion[self.kwargs["LK"]]/residuo.fraccion[self.kwargs["LK"]]*residuo.fraccion[self.kwargs["HK"]]/self.entrada.fraccion[self.kwargs["HK"]])*log((alfa_b*alfa_f)**0.5)/log((alfa_d*alfa_f)**0.5)
        else:                               #Ec. de Kirkbride
            ratio=(self.entrada.fraccion[self.kwargs["HK"]]/self.entrada.fraccion[self.kwargs["LK"]]*residuo.fraccion[self.kwargs["LK"]]**2/destilado.fraccion[self.kwargs["HK"]]**2*residuo.caudalmolar/destilado.caudalmolar)**0.206

        self.Ns=self.NTray/(ratio+1)
        self.Nr=self.NTray-self.Ns
        self.N_feed=unidades.Dimensionless(self.Ns+1)

        if self.kwargs["condenser"]:      #Parcial
            Tout=destilado.eos._Dew_T()
        else:
            Tout=destilado.eos._Bubble_T()
        Tin=destilado.eos._Dew_T()

        SalidaDestilado=destilado.clone(T=Tout)

#FIXME: o el ejemplo está mal planteado o este valor es ilógico
        ToutReboiler=residuo.eos._Bubble_T()
        ToutReboiler2=residuo.eos._Dew_T()
        print ToutReboiler, ToutReboiler2, Tin, Tout
        SalidaResiduo=residuo.clone(T=ToutReboiler)
        self.salida=[SalidaDestilado, SalidaResiduo]

        inCondenser=destilado.clone(T=Tin, P=self.entrada.P, split=self.RCalculada+1)
        outCondenser=destilado.clone(T=Tout, P=self.entrada.P, split=self.RCalculada+1)
        self.DutyCondenser=unidades.Power(outCondenser.h-inCondenser.h)
        self.DutyReboiler=unidades.Power(SalidaDestilado.h+SalidaResiduo.h-self.DutyCondenser-self.entrada.h)

        self.DestiladoT=SalidaDestilado.T
        self.DestiladoP=SalidaDestilado.P
        self.DestiladoMassFlow=SalidaDestilado.caudalmasico
        self.DestiladoMolarComposition=SalidaDestilado.fraccion
        self.ResiduoT=SalidaResiduo.T
        self.ResiduoP=SalidaResiduo.P
        self.ResiduoMassFlow=SalidaResiduo.caudalmasico
        self.ResiduoMolarComposition=SalidaResiduo.fraccion
        self.LKName=self.salida[0].componente[self.kwargs["LK"]].nombre
        self.HKName=self.salida[0].componente[self.kwargs["HK"]].nombre

    def McCabe(self):
        return Tower.McCabe(self, self.kwargs["LK"], self.kwargs["HK"])

    def propTxt(self):
        txt="#---------------"+QApplication.translate("pychemqt", "Calculate properties")+"-----------------#"+os.linesep
        txt+=os.linesep+"%-25s\t%s" %(QApplication.translate("pychemqt", "Top Output Temperature"), self.salida[0].T.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Top Output Pressure"), self.salida[0].P.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Top Output Mass Flow"), self.salida[0].caudalmolar.str)+os.linesep
        txt+="#"+QApplication.translate("pychemqt", "Top Output Molar Composition")+os.linesep
        for componente, fraccion in zip(self.salida[0].componente, self.salida[0].fraccion):
            txt+="%-25s\t %0.4f" %(componente.nombre, fraccion)+os.linesep

        txt+=os.linesep+"%-25s\t%s" %(QApplication.translate("pychemqt", "Bottom Output Temperature"), self.salida[1].T.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Bottom Output Pressure"), self.salida[1].P.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Bottom Output Mass Flow"), self.salida[1].caudalmolar.str)+os.linesep
        txt+="#"+QApplication.translate("pychemqt", "Bottom Output Molar Composition")+os.linesep
        for componente, fraccion in zip(self.salida[1].componente, self.salida[1].fraccion):
            txt+="%-25s\t %0.4f" %(componente.nombre, fraccion)+os.linesep

        txt+=os.linesep+"%-25s\t %s" %(QApplication.translate("pychemqt", "Feed Calculate method"), self.TEXT_FEED[self.kwargs["feed"]])+os.linesep
        txt+="%-25s\t %s" %(QApplication.translate("pychemqt", "Condenser type"), self.TEXT_CONDENSER[self.kwargs["condenser"]])+os.linesep
        txt+="%-25s\t %s" %(QApplication.translate("pychemqt", "Light Key Component"), self.salida[0].componente[self.kwargs["LK"]].nombre)+os.linesep
        txt+="%-25s\t %s" %(QApplication.translate("pychemqt", "Heavy Key Component"), self.salida[0].componente[self.kwargs["HK"]].nombre)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Minimum Reflux Ratio"), self.Rmin.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Reflux Ratio"), self.RCalculada.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Stage Number"), self.NTray.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Feed Stage"), self.N_feed.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Condenser Duty"), self.DutyCondenser.str)+os.linesep
        txt+="%-25s\t%s" %(QApplication.translate("pychemqt", "Reboiler Duty"), self.DutyReboiler.str)+os.linesep

        return txt

    @classmethod
    def propertiesEquipment(cls):
        list=[(QApplication.translate("pychemqt", "Top Output Temperature"), "DestiladoT", unidades.Temperature),
                (QApplication.translate("pychemqt", "Top Output Pressure"), "DestiladoP", unidades.Pressure),
                (QApplication.translate("pychemqt", "Top Output Mass Flow"), "DestiladoMassFlow", unidades.MassFlow),
                (QApplication.translate("pychemqt", "Top Output Molar Composition"), "DestiladoMolarComposition", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Bottom Output Temperature"), "ResiduoT", unidades.Temperature),
                (QApplication.translate("pychemqt", "Bottom Output Pressure"), "ResiduoP", unidades.Pressure),
                (QApplication.translate("pychemqt", "Bottom Output Mass Flow"), "ResiduoMassFlow", unidades.MassFlow),
                (QApplication.translate("pychemqt", "Bottom Output Molar Composition"), "ResiduoMolarComposition", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Feed Calculate method"), ("TEXT_FEED", "feed"), str),
                (QApplication.translate("pychemqt", "Condenser type"), ("TEXT_CONDENSER", "condenser"), str),
                (QApplication.translate("pychemqt", "Light Key Component"), "LKName", str),
                (QApplication.translate("pychemqt", "Heavy Key Component"), "HKName", str),
                (QApplication.translate("pychemqt", "Minimum Reflux Ratio"), "Rmin", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Reflux Ratio"), "RCalculada", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Stage Number"), "NTray", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Feed Stage"), "N_feed", unidades.Dimensionless),
                (QApplication.translate("pychemqt", "Condenser Duty"), "DutyCondenser", unidades.Power),
                (QApplication.translate("pychemqt", "Reboiler Duty"), "DutyReboiler", unidades.Power)]
        return list

    def propertiesListTitle(self, index):
        """Define los titulos para los popup de listas"""
        lista=[comp.nombre for comp in self.kwargs["entrada"].componente]
        return lista



def batch():
    # Plugging-in contant values
    D = 10
    a = 2.41
    W_int = 100
    x_w_int = 0.5

    t = range(0, 6, 1)

    # Defining function for integration
    def batch(x_w, t):
        W_t = -D*t + W_int
        y = a*x_w/ (1.0 + x_w*(a-1.0))

        dx_wdt = -(D/W_t)*(y - x_w)
        return dx_wdt

    x_w_sol = odeint(batch, x_w_int, t)

    # Plotting the solution
    figure()
    plot(t, x_w_sol, '-o')
    xlabel('Time, hours')
    ylabel('x_w')
    grid()
    plt.show()





if __name__ == '__main__':

#    agua=Corriente(T=300, P=101325., caudalMasico=1000, ids=[4, 5, 6, 7, 8, 10, 11, 12, 13], fraccionMolar=[0.02361538, 0.2923077, 0.3638462, 0.02769231, 0.01153846, 0.01769231, 0.03007692, 0.2093846, 0.02384615])
#    columna=ColumnFUG(entrada=agua, LK=2, LKsplit=0.9, HK=3, HKsplit=0.9, R_Rmin=1.05, calc_feed=0, DeltaP=0.1)
#    print columna.Rmin
#    print columna.DutyCondenser.MJh, columna.DutyReboiler.MJh

#    blend=Corriente(T=340, P=101325, caudalMasico=1, fraccionMolar=[0.3, 0.5, 0.05, 0.15])
#    columna=ColumnFUG(entrada=blend, LK=0, LKsplit=0.9866, HK=3, HKsplit=0.639, R_Rmin=1.1, feed=0)

    T = unidades.Temperature(205, "F")
    P = unidades.Pressure(315, "psi")
    blend=Corriente(T=T, P=P, caudalMasico=1, fraccionMolar=[0.26, 0.09, 0.25, 0.17, 0.11, 0.12])
#    columna=ColumnFUG(entrada=blend, LK=0, LKsplit=0.96666, HK=3, HKsplit=0.95, R_Rmin=1.2)
#    print columna.DutyCondenser
    print blend.mezcla.ids
#    entrada=Corriente(T=340, P=101325, caudalMasico=0.01, ids=[10, 38, 22, 61], fraccionMolar=[.3, 0.5, 0.05, 0.15])
#    flash=Flash(entrada=entrada)
#    print flash.status, flash.msg

#    from scipy import *
#    from scipy.integrate import odeint
#    from pylab import *
#    import matplotlib.pyplot as plt
#    batch()

