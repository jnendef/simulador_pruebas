import logging
import numpy as np

# ''' Niveles de logging
# Para obtener _TODO_ el detalle: level=logging.info
# Para comprobar los posibles problemas level=logging.warning
# Para comprobar el funcionamiento: level=logging.DEBUG
# '''

#
# Objeto DTO (data object transfer).
# 
# @author fgregorio
#
# @traductor jnaveiro
#


def coeficientConsumMax(Coef, bmax,pobreza):
    Cmax=np.max(Coef)
    if np.sum(Coef) == 0.0:
        suma = 1.0
    else:
        suma = np.sum(Coef)
        
    control= Cmax/suma
    n= len(Coef)
    betas = n*bmax - (1-pobreza)

    if control>bmax and betas >= 0.0:
        Caux = Cmax - Coef

        if np.sum(Caux) == 0.0:
            Caux[:] = 0.1
        
        suma2 = np.sum(Caux)

        cc = Caux/suma2
        cc *= (-1*betas) 
        cc += bmax
    else:
        if np.max(Coef) <= 0.0:
            cc = (np.ones(len(Coef))/(len(Coef)))*(1-pobreza)
        else:
            cc=(Coef/suma)*(1-pobreza)
        
    return cc

def coeficientConsumMin(Consum, bmin,pobreza):
    Cmin=np.min(Consum)
    if np.sum(Consum) == 0.0:
        suma = 1.0
    else:
        suma = np.sum(Consum)
        
    control= Cmin/suma
    n= len(Consum)
    betas=(1-pobreza)-bmin*n

    if control<bmin and betas >= 0.0:
        Caux=Consum - Cmin

        if np.sum(Caux) == 0.0:
            Caux[:] = 0.1
        
        suma2 = np.sum(Caux)

        cc = Caux/suma2
        cc *= betas 
        cc += bmin
    else:
        if np.max(Consum) <= 0.0:
            cc = (np.ones(len(Consum))/(len(Consum)))*(1-pobreza)
        else:
            cc=(Consum/suma)*(1-pobreza)
        
    return cc

def combinado(Consumos,bmin,bmax,pobreza):
    coef1 = coeficientConsumMax(Consumos,bmax,pobreza)
    coef2 = coeficientConsumMin(coef1,bmin,pobreza)
    return coef2

class ComunidadEnergeticaDTO:
    """
    author: fgregorio

    traductor: jnaveiro

    Definición: Esta clase pertenece al grupo DTO(data object transfer). Su misión es transmitir la información de los usuarios de las comunidades energéticas.
    
    Propiedades:

        1.idComunidadEnergetica
        2.dsComunidadEnergetica
        3.usuariosComunidad
        4.generadoresComunidad
        5.cuotaParticipacion_min
        6.cuotaParticipacion_max
        7.porcentajeDedicadoPobrezaEnergetica
    
    Métodos:

         1. ComunidadEnergeticaDTO.obtenerCoeficientesReparto_normalizadoByDemandaEnergia
         2. ComunidadEnergeticaDTO.obtenerCoeficientesReparto_cumplirCondiciones_cuotaMinima
         3. ComunidadEnergeticaDTO.obtenerCoeficientesReparto_cumplirCondiciones_cuotaMaxima
         4. ComunidadEnergeticaDTO.obtenerPrevisionEnergiaAsignadaByCoeficientesReparto
         5. ComunidadEnergeticaDTO.obtenerPrevisionExcedenteAsignadoByCoeficientesReparto
         6. ComunidadEnergeticaDTO.obtenerCuotaUtilizacionUsuariosComunidadEnergetica
         7. ComunidadEnergeticaDTO.imprimirCoeficientesRepartoClientes
         8. ComunidadEnergeticaDTO.imprimirPrevisionEnergiaAsignadaByCoeficientesReparto
         9. ComunidadEnergeticaDTO.imprimirPrevisionExcedenteAsignadoByCoeficientesReparto
        10. ComunidadEnergeticaDTO.imprimirCuotaUtilizacionComunidadEnergetica
        11. ComunidadEnergeticaDTO.getIdComunidadEnergetica
        12. ComunidadEnergeticaDTO.setIdComunidadEnergetica
        13. ComunidadEnergeticaDTO.getDsComunidadEnergetica
        14. ComunidadEnergeticaDTO.setDsComunidadEnergetica
        15. ComunidadEnergeticaDTO.getUsuariosComunidad
        16. ComunidadEnergeticaDTO.setUsuariosComunidad
        17. ComunidadEnergeticaDTO.getGeneradoresComunidad
        18. ComunidadEnergeticaDTO.setGeneradoresComunidad
        19. ComunidadEnergeticaDTO.getCuotaParticipacion_min
        20. ComunidadEnergeticaDTO.setCuotaParticipacion_min
        21. ComunidadEnergeticaDTO.getCuotaParticipacion_max
        22. ComunidadEnergeticaDTO.setCuotaParticipacion_max
        23. ComunidadEnergeticaDTO.getPorcentajeDedicadoPobrezaEnergetica
        24. ComunidadEnergeticaDTO.setPorcentajeDedicadoPobrezaEnergetica
        """
    # 
    # Atributos correspondientes a la comunidad energética 
    # 
    def __init__(self,idComunidadEnergetica = "",dsComunidadEnergetica = "", dias = 366, horas = 24):
        self.dias = dias
        self.horas = horas
        self.idComunidadEnergetica = idComunidadEnergetica
        self.dsComunidadEnergetica = dsComunidadEnergetica
        self.usuariosComunidad = []
        self.generadoresComunidad = []
        self.cuotaParticipacion_min = 0 # No puede ser > 100/numClientes
        self.cuotaParticipacion_max = 100 # No puede ser < 100/numClientes
        self.porcentajeDedicadoPobrezaEnergetica = 0

    def variacionObtencionCoef(self):
        dias = self.dias
        horas = self.horas
        usuariosComunidad = self.getUsuariosComunidad()
        MatrizConsumos = np.zeros((dias,horas,len(usuariosComunidad)))
        for it_cliente in range(len(usuariosComunidad)):
            matrizConsumos = np.zeros((dias,horas))
            usuarioAux =usuariosComunidad[it_cliente]
            consumosAux = usuarioAux.getConsumos()
            for it_dia in range(dias):
                for it_hora in range(horas):
                    if(consumosAux[it_dia][it_hora] != None):
                        consumo_diaHora = usuariosComunidad[it_cliente].getConsumos()[it_dia][it_hora].getValorDatoConsumoHorario()
                        matrizConsumos[it_dia,it_hora] = consumo_diaHora
            
            MatrizConsumos[:,:,it_cliente] = matrizConsumos[:,:]
        
        for it_dia in range(dias):
            for it_hora in range(horas):
                minimo = 0.01 * self.cuotaParticipacion_min
                maxima = 0.01 * self.cuotaParticipacion_max
                pobreza = 0.01*self.getPorcentajeDedicadoPobrezaEnergetica()
                MatrizBetas = combinado(MatrizConsumos[it_dia,it_hora,:] , minimo, maxima, pobreza)

                for it_cliente in range(len(usuariosComunidad)):
                    usuariosComunidad[it_cliente].getCoeficientesReparto()[it_dia][it_hora] = 100*MatrizBetas[it_cliente]


    def obtenerCoeficientesReparto_normalizadoByDemandaEnergia (self):
        """
        Definición: Método encargado de obtener los coeficientes de reparto a partir de los consumos de los diversos clientes de la comunidad energética. Se calcula obteniendo para cada hora de cada día el consumo total para después dividir el consumo de cada usuario para esa hora de ese día entre el consumo total.
        
        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas:

            1. usuariosComunidad (Coeficientes de reparto)
        """
        
        #     Recorremos cada día y hora, obteniendo el coeficiente de reparto para cada cliente
        dias = self.dias
        horas = self.horas
        for it_dia in range(dias):
            for it_hora in range(horas):

                #     Declaramos la variable que contendrá el total del consumo de la comunidad para esa hora
                consumoTotalComunidad_diaHora = 0.0
                
                #     Realizamos una iteración por los clientes para obtener el total del consumo previsto para la comunidad
                usuariosComunidad = self.getUsuariosComunidad()
                for it_cliente in range(len(usuariosComunidad)):
                    usuarioAux =usuariosComunidad[it_cliente]
                    consumosAux = usuarioAux.getConsumos()
                    if(consumosAux[it_dia][it_hora] != None):
                        consumoTotalComunidad_diaHora = consumoTotalComunidad_diaHora + usuariosComunidad[it_cliente].getConsumos()[it_dia][it_hora].getValorDatoConsumoHorario()
                
                #     Paso 1: Recorremos de nuevo para asignar el coeficiente de reparto para cada cliente
                for it_cliente in range(len(usuariosComunidad)):
                    if(usuariosComunidad[it_cliente].getConsumos()[it_dia][it_hora] != None):
                        if consumoTotalComunidad_diaHora!=0:
                        
                            coeficiente_base = (usuariosComunidad[it_cliente].getConsumos()[it_dia][it_hora].getValorDatoConsumoHorario () / consumoTotalComunidad_diaHora)
                        else:
                            coeficiente_base = 100/len(usuariosComunidad)
                        
                        pobreza_energ = (100 - self.getPorcentajeDedicadoPobrezaEnergetica())
                        usuariosComunidad[it_cliente].getCoeficientesReparto()[it_dia][it_hora] = coeficiente_base * pobreza_energ

    def obtenerCoeficientesReparto_cumplirCondiciones_cuotaMinima (self, iterar_metodo: bool, numInteracion: int):
        """
        Definición: Método encargado de hacer cumplir el mínimo establecido en los coeficientes de reparto. Lo que se hace es imponer el valor de cuota mínima a aquellos coeficientes cuyo valor sea menor. Es un proceso iterativo en el que se reducen las ganancias de todos los usuarios que pasen del mínimo para ayudar a los que no llegan a ese mínimo. Para ello, además de imponer el valor de cuota mínima, calcula qué porcentaje se necesita retirar de los demás usuarios y reparte lo que hay que retirar entre todos ellos. Tiene que realizar esta iteración varias veces hasta que ningún usuario esté por debajo del mínimo. La cuota mínima debe de ser menor que 100/(Número de usuarios de la comunidad), sino no converge.
        
        Variables de entrada: iterar_metodo: bool, numInteracion: int

        Variables de salida: Ninguna

        Propiedades modificadas:

            1. usuariosComunidad (Coeficientes de reparto)
        """
        
        #     Recorremos cada día y hora, obteniendo el coeficiente de reparto para cada cliente
        
        dias = self.dias
        horas = self.horas

        for it_dia in range(dias):
            for it_hora in range(horas):

                #     PASO 1: Chequemos quien y cuanto cumple o no cumple. 
                diferenciaCoeficienteTotal_noCumple_minimo = 0.0
                diferenciaCoeficienteTotal_siCumple_minimo = 0.0
                #     Recorremos obteniendo los datos preliminales
                for it_cliente in range(len(self.usuariosComunidad)):
                    cliente_it = self.getUsuariosComunidad()[it_cliente]
                    coeficienteReparto= cliente_it.getCoeficientesReparto()[it_dia][it_hora]
                    minimoRepartoCoeficiente = self.getCuotaParticipacion_min()

                    if(coeficienteReparto<=minimoRepartoCoeficiente):
                        diferenciaCoeficienteTotal_noCumple_minimo = diferenciaCoeficienteTotal_noCumple_minimo + (minimoRepartoCoeficiente - coeficienteReparto)
                        cliente_it.getCoeficientesReparto()[it_dia][it_hora] = minimoRepartoCoeficiente
                    else:
                        diferenciaCoeficienteTotal_siCumple_minimo = diferenciaCoeficienteTotal_siCumple_minimo + coeficienteReparto

                #     fin for

                #     Condición método recursivo
                if(diferenciaCoeficienteTotal_noCumple_minimo != 0 ): #  No hay ninguna diferencia y hemos acabado
                    
                    # Paso 2: Recorremos únicamente los que son mayores que el mímimo restandole lo que falta de manera podenderada
                    for it_cliente in range(len(self.usuariosComunidad)):
                        
                        cliente_it = self.getUsuariosComunidad()[it_cliente]
                        coeficienteReparto= cliente_it.getCoeficientesReparto()[it_dia][it_hora]
                        minimoRepartoCoeficiente = self.getCuotaParticipacion_min()
                        
                        

                        if(coeficienteReparto>minimoRepartoCoeficiente): #  Es decir, que tiene margen
                            cliente_it.getCoeficientesReparto()[it_dia][it_hora] = cliente_it.getCoeficientesReparto()[it_dia][it_hora] - (cliente_it.getCoeficientesReparto()[it_dia][it_hora]/diferenciaCoeficienteTotal_siCumple_minimo) * diferenciaCoeficienteTotal_noCumple_minimo
                        
                    
                    
                    # Como no sabemos si con el cambio hemos estropeado alguno que antes SI cumplia, iteramos
                    if(iterar_metodo and numInteracion <5):
                        
                        #     Imprimimos tras cada iteración el resultado particial que llevamos
                        #     self.imprimirCoeficientesRepartoClientes()
                        
                        # print("Ejecutamos una nueva iteracion del metodo participacionMinima")
                        # print("Iteracion", numInteracion)
                        self.obtenerCoeficientesReparto_cumplirCondiciones_cuotaMinima(iterar_metodo, numInteracion+1)
                    
                    # elif numInteracion >=20:
                    #     iterar_metodo = False
                    #     return iterar_metodo
                    # else:
                    #     return numInteracion
                    
                #     fin if
            #    for hora
        #     for dia

    def obtenerCoeficientesReparto_cumplirCondiciones_cuotaMaxima (self, iterar_metodo: bool, numInteracion: int):
        """
        Definición: Método encargado de hacer cumplir el máximo establecido en los coeficientes de reparto.. Lo que hace es imponer que el valor de cuota Máxima a aquellos que superen este valor. Es un proceso iterativo en el que se reduce las ganancias de  los usuarios que pasen del máximo para para repartirlo. Para ello, además de imponer la cuota máxima, calcula qué porcentaje se añade a los demás usuarios y reparte lo que hay entre todos ellos. Tiene que realizar esta iteración varias veces hasta que ningún usuario esté por encima del máximo. La cuota máxima debe de ser mayor que 100/(Número de usuarios de la comunidad), sino no converge
        
        Variables de entrada: iterar_metodo: bool, numInteracion: int

        Variables de salida: Ninguna

        Propiedades modificadas:

            1. usuariosComunidad (Coeficientes de reparto)
        """
                
        
        # logging.info("Cálculo del máximo")
        #     Recorremos cada día y hora, obteniendo el coeficiente de reparto para cada cliente
            
        #     Obtenemos el máximo del coeficiente de reparto para la comunidad
        maximoRepartoCoeficiente = float(self.getCuotaParticipacion_max())
        
        dias = self.dias
        horas = self.horas

        for it_dia in range(dias):
            for it_hora in range(horas):

                #     PASO 1: Chequemos quien y cuanto cumple o no cumple. 
                diferenciaCoeficienteTotal_noCumple_maximo = 0.0
                diferenciaCoeficienteTotal_siCumple_maximo = 0.0
                #     Recorremos obteniendo los datos preliminales
                for it_cliente in range(len(self.usuariosComunidad)):
                    cliente_it = self.getUsuariosComunidad()[it_cliente]
                    coeficienteReparto = cliente_it.getCoeficientesReparto()[it_dia][it_hora]

                    if(coeficienteReparto>=maximoRepartoCoeficiente):
                        #Modificado 08/05/2024: (coeficienteReparto - maximoRepartoCoeficiente) Se cambiaron las posiciones.
                        diferenciaCoeficienteTotal_noCumple_maximo = diferenciaCoeficienteTotal_noCumple_maximo + (coeficienteReparto - maximoRepartoCoeficiente)
                        cliente_it.getCoeficientesReparto()[it_dia][it_hora] = maximoRepartoCoeficiente
                    else:
                        diferenciaCoeficienteTotal_siCumple_maximo = diferenciaCoeficienteTotal_siCumple_maximo + coeficienteReparto
                    
                 #     fin for
                
                #     Condición método recursivo
                if(diferenciaCoeficienteTotal_noCumple_maximo!=0 ):
                    #     No hay ninguna diferencia y hemos acabado
                    
                    #     Paso 2: Recorremos únicamente los que son mayores que el mímimo restandole lo que falta de manera podenderada
                    for it_cliente in range(len(self.usuariosComunidad)):
                        
                        
                        cliente_it = self.getUsuariosComunidad()[it_cliente]
                        coeficienteReparto= cliente_it.getCoeficientesReparto()[it_dia][it_hora]

                        # fecha = cliente_it.getConsumos()[it_dia][it_hora].getFcDatoConsumoHorario()
                        
                        # logging.info("cliente "+str(it_cliente))
                        # logging.info("fecha: "+str(cliente_it.getConsumos()[it_dia][it_hora].getFcDatoConsumoHorario()))
                        # logging.info("consumo: "+str(cliente_it.getConsumos()[it_dia][it_hora].getValorDatoConsumoHorario()))
                        # logging.info("Coef: "+str(coeficienteReparto))
                        

                        if(coeficienteReparto<maximoRepartoCoeficiente): #     Es decir, que tiene margen
                            
                            cliente_it.getCoeficientesReparto()[it_dia][it_hora] = cliente_it.getCoeficientesReparto()[it_dia][it_hora] + (cliente_it.getCoeficientesReparto()[it_dia][it_hora]/diferenciaCoeficienteTotal_siCumple_maximo) * diferenciaCoeficienteTotal_noCumple_maximo
                    
                    
                    #     Como no sabemos si con el cambio hemos estropeado alguno que antes SI cumplia, iteramos
                    if(iterar_metodo and numInteracion <5 ):
                        
                        #     Imprimimos tras cada iteración el resultado particial que llevamos
                        #    self.imprimirCoeficientesRepartoClientes()
                        
                        # print("Ejecutamos una nueva iteracion del metodo participacionMaxima")
                        # print("Iteracion: ", numInteracion)
                        self.obtenerCoeficientesReparto_cumplirCondiciones_cuotaMaxima(iterar_metodo, numInteracion+1)

                    # elif numInteracion >=20:
                    #     iterar_metodo = False
                    #     return iterar_metodo
                    # else:
                    #     return numInteracion

                    
                #     fin if
             #    for hora
         #     for dia

    def obtenerPrevisionEnergiaAsignadaByCoeficientesReparto (self):
        """
        Definición: Método encargado de obtener la previsión de energía para cada usuario en función de su coeficiente de reparto. A partir de la generación prevista, teniendo los coeficientes de reparto ya calculados, multiplica la generación total por el coeficiente correspondiente.
        
        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas:

            1. usuariosComunidad (Energía de reparto)
        """
        #     Recorremos cada día y hora, obteniendo el coeficiente de reparto para cada cliente
        
        dias = self.dias
        horas = self.horas
        #     Realizamos una iteración por los clientes para obtener el total del consumo previsto para la comunidad
        usuariosComunidad = self.getUsuariosComunidad()
        for it_cliente in range(len(usuariosComunidad)):
            
            #     Creamos la matriz a rellenar con los valores del reparto de energía
            energiaRepartirCliente = [[None for i in range(horas)] for j in range(dias)]

            for it_dia in range(dias):
                for it_hora in range(horas):
    
                    #     Obtenemos la previsión de energía disponible
                    totalGeneracionEnergiaPrevista_diahora = 0.0
                    listGeneradores = self.getGeneradoresComunidad()
                    for it_generadores in range(len(listGeneradores)):
                        totalGeneracionEnergiaPrevista_diahora = totalGeneracionEnergiaPrevista_diahora + listGeneradores[it_generadores].getGeneracion()[it_dia][it_hora]
                    
                    
                    coeficienteRepartoCliente = usuariosComunidad[it_cliente].getCoeficientesReparto()[it_dia][it_hora]
                    energiaDisponibleClienteDiaHora = (coeficienteRepartoCliente/100) * totalGeneracionEnergiaPrevista_diahora
                    energiaRepartirCliente [it_dia][it_hora] = energiaDisponibleClienteDiaHora
                    
                 #    for hora
             #     for dia
        
            usuariosComunidad[it_cliente].setEnergiaReparto(energiaRepartirCliente)
        
        #     for cliente

    def obtenerPrevisionExcedenteAsignadoByCoeficientesReparto (self):
        """
        Definición: Método encargado de obtener los excedentes del cliente en base a su consumo. Teniendo la energía que le corresponde a cada usuario de la generada, calcula si el usuario tiene excedentes.
        
        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas:

            1. usuariosComunidad (Energía de reparto excedentes)
        """
                
        #     Recorremos cada día y hora, obteniendo el coeficiente de reparto para cada cliente
        
        dias = self.dias
        horas = self.horas

        #     Realizamos una iteración por los clientes para obtener el total del consumo previsto para la comunidad
        usuariosComunidad = self.getUsuariosComunidad()
        for it_cliente in range(len(usuariosComunidad)):
            
            #     Creamos la matriz a rellenar con los valores del reparto de energía
            excedenteEnergia = [[None for i in range(horas)] for j in range(dias)]
            
            for it_dia in range(dias):
                for it_hora in range(horas):
                    consumoClienteDiaHora = 0.0
                    if(usuariosComunidad[it_cliente].getConsumos()[it_dia][it_hora] != None):
                        consumoClienteDiaHora = usuariosComunidad[it_cliente].getConsumos()[it_dia][it_hora].getValorDatoConsumoHorario()
                    energiaAsignadaClienteDiaHora =  usuariosComunidad[it_cliente].getEnergiaReparto()[it_dia][it_hora]
                    excedenteEnergiaClienteDiaHora = energiaAsignadaClienteDiaHora - consumoClienteDiaHora
                    if(excedenteEnergiaClienteDiaHora<0):
                        excedenteEnergiaClienteDiaHora = 0
                    
                    excedenteEnergia [it_dia][it_hora] = excedenteEnergiaClienteDiaHora
                    
                #    for hora
            #     for dia
        
            usuariosComunidad[it_cliente].setEnergiaReparto_excedentes(excedenteEnergia)
        
        #     for cliente

    def obtenerCuotaUtilizacionUsuariosComunidadEnergetica (self):
        """
        Definición: Método encargado de calcular la cuota de participación base a los coeficientes de reparto del cliente. Calcula el promedio de participación de cada usuario.
        
        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas:

            1. usuariosComunidad (Cuota de participación a partir de los coeficientes de reparto)
        """
        #     Recorremos cada día y hora, obteniendo el coeficiente de reparto para cada cliente

        
        dias = self.dias
        horas = self.horas

        #     Realizamos una iteración por los clientes para obtener el total del consumo previsto para la comunidad
        usuariosComunidad = self.getUsuariosComunidad()
        for it_cliente in range(len(usuariosComunidad)):
            
            #     Creamos la matriz a rellenar con los valores del reparto de energía
            contadorCuotasParticipacion = 0
            cuotaParticipacionCalculadaCE = 0.0
            
            for it_dia in range(dias):
                for it_hora in range(horas):
                    if (usuariosComunidad[it_cliente].getConsumos()[it_dia][it_hora] != None):
                        contadorCuotasParticipacion += 1
                        cuotaParticipacionCalculadaCE = cuotaParticipacionCalculadaCE + usuariosComunidad[it_cliente].getCoeficientesReparto()[it_dia][it_hora]
                 #    for hora
             #     for dia

            try:
                usuariosComunidad[it_cliente].setCuotaParticipacion_calculadaCR(cuotaParticipacionCalculadaCE/contadorCuotasParticipacion)
            except ZeroDivisionError as e:
                logging.debug("Error en el paso de obtencion de cuota de participacion:")
                logging.debug(str(e))
                usuariosComunidad[it_cliente].setCuotaParticipacion_calculadaCR(0.0)
        
        #     for cliente

    def imprimirCoeficientesRepartoClientes (self):
        """
        Definición: Método utilizado para imprimir por archivo log la estructura de datos correspondiente al coeficiente de reparto.
        
        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas: Ninguna
        """
        
        dias = self.dias
        horas = self.horas

        usuariosComunidad = self.getUsuariosComunidad()
        for it_cliente in range(len(usuariosComunidad)):
            logging.info("\n")
            logging.info(" Cliente: " , usuariosComunidad[it_cliente].getIdUsuario())
            logging.info("\n")
            for it_dia in range(dias):
                for it_hora in range(horas):
                    logging.info("Coeficiente reparto [" + str(it_dia) + "] [" + str(it_hora) + "]:" + str(usuariosComunidad[it_cliente].getCoeficientesReparto()[it_dia][it_hora]))

    def imprimirPrevisionEnergiaAsignadaByCoeficientesReparto (self):
        """
        Definición: Método utilizado para imprimir por log el reparto de energía de los clientes.
        
        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas: Ninguna
        """
        
        dias = self.dias
        horas = self.horas

        usuariosComunidad = self.getUsuariosComunidad()
        for it_cliente in range(len(usuariosComunidad)):
            logging.info("\n")
            logging.info(" Cliente: " , usuariosComunidad[it_cliente].getIdUsuario())
            logging.info("\n")
            for it_dia in range(dias):
                for it_hora in range(horas):
                    logging.info("Energia asignada cliente [hora][dia]: [" + str(it_dia) + "] [" + str(it_hora) + "]:" + str(usuariosComunidad[it_cliente].getEnergiaReparto()[it_dia][it_hora]))

    def imprimirPrevisionExcedenteAsignadoByCoeficientesReparto (self):
        """
        Definición: Método empleado para imprimir por log los excedentes de energía de los clientes respecto su demanda energética.
        
        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas: Ninguna
        """
        
        dias = self.dias
        horas = self.horas

        usuariosComunidad = self.getUsuariosComunidad()
        for it_cliente in range(len(usuariosComunidad)):
            logging.info("\n")
            logging.info(" Cliente: " + str(usuariosComunidad[it_cliente].getIdUsuario()))
            logging.info("\n")
            for it_dia in range(dias):
                for it_hora in range(horas):
                    logging.info("Energia excedente cliente [hora][dia]: [" + str(it_dia) + "] [" + str(it_hora) + "]:" + str(usuariosComunidad[it_cliente].getEnergiaReparto_excedentes()[it_dia][it_hora]))

    def imprimirCuotaUtilizacionComunidadEnergetica (self):
        """
        Definición: Método utilizado para imprimir por log el coeficiente de participación de los clientes en base a su coeficiente de reparto dinámico.

        Variables de entrada: Ninguna

        Variables de salida: Ninguna

        Propiedades modificadas: Ninguna
        """
        usuariosComunidad = self.getUsuariosComunidad()
        for it_cliente in range(len(usuariosComunidad)):
            logging.info("Cuota de utilización calculada (en base a los CR): Cliente " + str(usuariosComunidad[it_cliente].getIdUsuario())+ " ( de perfil " + str(usuariosComunidad[it_cliente].getCupsUsuario()).split("-")[0] + ") : " + str(usuariosComunidad[it_cliente].getCuotaParticipacion_calculadaCR()))

    def getIdComunidadEnergetica(self):
        return self.idComunidadEnergetica

    def setIdComunidadEnergetica(self, idComunidadEnergetica: str):
        self.idComunidadEnergetica = idComunidadEnergetica

    def getDsComunidadEnergetica(self):
        return self.dsComunidadEnergetica

    def setDsComunidadEnergetica(self, dsComunidadEnergetica: str):
        self.dsComunidadEnergetica = dsComunidadEnergetica

    def getUsuariosComunidad(self):
        return self.usuariosComunidad

    def setUsuariosComunidad(self, usuariosComunidad):
        self.usuariosComunidad = usuariosComunidad

    def getGeneradoresComunidad(self):
        return self.generadoresComunidad

    def setGeneradoresComunidad(self, generadoresComunidad):
        self.generadoresComunidad = generadoresComunidad

    def getCuotaParticipacion_min(self):
        return self.cuotaParticipacion_min

    def setCuotaParticipacion_min(self,cuotaParticipacion_min: float):
        self.cuotaParticipacion_min = cuotaParticipacion_min

    def getCuotaParticipacion_max(self):
        return self.cuotaParticipacion_max

    def setCuotaParticipacion_max(self,cuotaParticipacion_max: float):
        self.cuotaParticipacion_max = cuotaParticipacion_max

    def getPorcentajeDedicadoPobrezaEnergetica(self):
        return self.porcentajeDedicadoPobrezaEnergetica
    
    def  setPorcentajeDedicadoPobrezaEnergetica(self, porcentajeDedicadoPobrezaEnergetica: float):
        self.porcentajeDedicadoPobrezaEnergetica = porcentajeDedicadoPobrezaEnergetica
