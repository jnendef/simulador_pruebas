
#*
# Objeto DTO (data object transfer).
# 
# @author fgregorio
#
# @traductor jnaveiro
#

class DatoConsumoUsuarioDTO:
    def __init__(self):
        self.idUserData = -1
        self.fcDatoConsumoHorario = ""
        self.valorDatoConsumoHorario = 0.0

    def getFcDatoConsumoHorario(self):
        return self.fcDatoConsumoHorario
    
    def setFcDatoConsumoHorario(self,fcDatoConsumoHorario:str):
        self.fcDatoConsumoHorario = fcDatoConsumoHorario
    
    def getValorDatoConsumoHorario(self):
        return self.valorDatoConsumoHorario
    
    def setValorDatoConsumoHorario(self,valorDatoConsumoHorario:float):
        self.valorDatoConsumoHorario = valorDatoConsumoHorario
    
    def getIdUserData(self):
        return self.idUserData
    
    def setIdUserData(self,idUserData:int):
        self.idUserData = idUserData
