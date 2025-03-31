import numpy as np

# 
# Objeto DTO (data object transfer).
# 
# @author fgregorio
# 
# @traductor jnaveiro

class UsuarioDTO:
    """
    author: fgregorio

    traductor: jnaveiro

    Definición: Esta clase pertenece al grupo DTO(data object transfer). Su misión es transmitir la información de los usuarios de las comunidades energéticas.
    
    Propiedades:

        1.idUsuario
        2.dsUsuario
        3.consumos
        4.coeficientesReparto
        5.energiaReparto
        6.energiaReparto_excedentes
        7.cuotaParticipacion_calculadaCR
    
    Métodos:

         1. UsuarioDTO.imprimirConsumosCliente
         2. UsuarioDTO.imprimirCoeficientesReparto
         3. UsuarioDTO.getIdUsuario
         4. UsuarioDTO.setIdUsuario
         5. UsuarioDTO.getDsUsuario
         6. UsuarioDTO.setDsUsuario
         7. UsuarioDTO.getConsumos
         8. UsuarioDTO.setConsumos
         9. UsuarioDTO.getCoeficientesReparto
        10. UsuarioDTO.setCoeficientesReparto
        11. UsuarioDTO.getEnergiaReparto
        12. UsuarioDTO.setEnergiaReparto
        13. UsuarioDTO.getEnergiaReparto_excedentes
        14. UsuarioDTO.setEnergiaReparto_excedentes
        15. UsuarioDTO.getCuotaParticipacion_calculadaCR
        16. UsuarioDTO.setCuotaParticipacion_calculadaCR
        17. UsuarioDTO.getConsumos
        18. UsuarioDTO.setConsumos
        """
    def __init__(self, Dias = 365, Horas = 24):
        self.idUsuario = ""
        self.dsUsuario = ""
        self.cupsUsuario = ""
        self.Dias = Dias
        self.Horas = Horas
        self.consumos = [[None for i in range(Horas)] for j in range(Dias)]
        self.coeficientesReparto = [[None for i in range(Horas)] for j in range(Dias)]
        self.energiaReparto =  [[None for i in range(Horas)] for j in range(Dias)]
        self.energiaReparto_excedentes =  [[None for i in range(Horas)] for j in range(Dias)]
        self.cuotaParticipacion_calculadaCR = 0

    # 
    # Método encargado de imprimir por pantalla los consumos de un Usuario
    # 
    def imprimirConsumosCliente (self):
        dimensiones = np.shape(self.consumos)
        for itDia in range(dimensiones[0]):
            for itHora in range(dimensiones[1]):
                print("[",itDia,"] [",itHora,"]", self.consumos[itDia][itHora])
        
    # 
    # Método encargado de imprimir por pantalla los coeficientes de reparto de un Usuario
    # 
    def imprimirCoeficientesReparto (self):
        dimensiones = np.shape(self.coeficientesReparto)
        for itDia in range(dimensiones[0]):
            for itHora in range(dimensiones[1]):
                print("[",itDia,"] [",itHora,"]" , self.coeficientesReparto[itDia][itHora])
        
    def getIdUsuario(self):
        return str(self.idUsuario)

    def setIdUsuario(self, idUsuario):
        self.idUsuario = idUsuario

    def getCupsUsuario(self):
        return str(self.cupsUsuario)

    def setCupsUsuario(self,cupsUsuario):
        self.cupsUsuario = cupsUsuario

    def getDsUsuario(self):
        return str(self.dsUsuario)

    def setDsUsuario(self,dsUsuario):
        self.dsUsuario = dsUsuario

    def getConsumos(self):
        return self.consumos

    def setConsumos(self,consumos):
        self.consumos = consumos

    def getCoeficientesReparto(self):
        return self.coeficientesReparto

    def setCoeficientesReparto(self, coeficientes):
        self.coeficientesReparto = coeficientes

    def getEnergiaReparto(self):
        return self.energiaReparto

    def setEnergiaReparto(self, energiaReparto):
        self.energiaReparto = energiaReparto

    def getEnergiaReparto_excedentes(self):
        return self.energiaReparto_excedentes

    def setEnergiaReparto_excedentes(self, energiaReparto_excedentes):
        self.energiaReparto_excedentes = energiaReparto_excedentes

    def getCuotaParticipacion_calculadaCR(self):
        return self.cuotaParticipacion_calculadaCR

    def setCuotaParticipacion_calculadaCR(self, cuotaParticipacion_calculadaCR):
        self.cuotaParticipacion_calculadaCR = cuotaParticipacion_calculadaCR

    def getConsumos(self):
        return self.consumos

    def setConsumos(self,consumos):
        self.consumos = consumos

