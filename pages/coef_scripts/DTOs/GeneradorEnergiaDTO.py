import numpy as np
# import accesos.AccesoCommons as AccesoCommons

#*
# Objeto DTO (data object transfer).
# 
# @author fgregorio
#
# @traductor jnaveiro
#


class GeneradorEnergiaDTO:
    def __init__(self,idGeneradorEnergia="",dsGeneradorEnergia="",Dias = 365,Horas = 24):
        self.idGeneradorEnergia = idGeneradorEnergia
        self.dsGeneradorEnergia = dsGeneradorEnergia
        self.Generacion = np.zeros((Dias,Horas))

    def getIdGeneradorEnergia(self):
        return str(self.idGeneradorEnergia)

    def setIdGeneradorEnergia(self, idGeneradorEnergia):
        self.idGeneradorEnergia = idGeneradorEnergia

    def getDsGeneradorEnergia(self):
        return str(self.dsGeneradorEnergia)

    def setDsGeneradorEnergia(self,dsGeneradorEnergia):
        self.dsGeneradorEnergia = dsGeneradorEnergia

    def getGeneracion(self):
        return self.Generacion

    def setGeneracion(self,Generacion):
        self.Generacion = Generacion
