# 
# Paso para la ejecucion de la simulacion de los coeficientes de reparto
# 
# @referencia fgregorio
# 
# @modificaciones jnaveiro
# 

from datetime import datetime as tiem 
import datetime as dt
import os

import pages.coef_scripts.agente_Basico as aB

import pages.coef_scripts.ComunidadesEnergeticasServicio as ComunidadesEnergeticasServicio

import logging
from logging.handlers import RotatingFileHandler


# Metodo para finalizar el proceso

def final1000(agente,fcStart,idComunidad):
    
    now = tiem.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S') 
    sentenciaUpdate = "UPDATE leading_db.energy_community_process"
    sentenciaUpdate = sentenciaUpdate+ " SET stop = '" + now + "',"
    sentenciaUpdate = sentenciaUpdate+ " result = 1000 "
    sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 40 AND start='"+ fcStart + "'"
    agente.ejecutar(sentenciaUpdate)
    agente.commitTransaction()

    return

def final1001(agente,fcStart,idComunidad):
    # Actulizamos la entrada correspondiente al proceso
        
    now = tiem.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S') 
    sentenciaUpdate = "UPDATE leading_db.energy_community_process"
    sentenciaUpdate = sentenciaUpdate+ " SET stop = '" + now + "',"
    sentenciaUpdate = sentenciaUpdate+ " result = 1001 "
    sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 40 AND start='"+ fcStart + "';"
    agente.ejecutar(sentenciaUpdate)
    agente.commitTransaction()
    
    return

# Funcion principal del paso 4

def Paso4(agente, Anyo, id_EnergyCommunity, bisiesto):
    """
    Definicion: Esta funcion es la principal de ejecucion del proceso de cálculo de coeficientes de reparto. Realiza las consultas a la base de datos y, una vez se tiene la informacion, calcula los coeficientes de reparto para actualizarlos en la base de datos.
    
    Variables de entrada: Agente, Anyo, id_EnergyCommunity, bisiesto
    
    Variables de salida: proceso, comunidadEnergetica
    
    Objetos relevantes:
    
        1. agenteEjecucionMySql
        2. comunidadEnergetica
    
    Librerías que se llaman:
    
        1. ComunidadesEnergeticasServicio
        2. agente_Basico
        3. datetime
        4. logging
        5. sys
        """
    #Variable para almacenar el id del proceso a ejecutar
    proceso = True

    # Variables globales
    dias = 365
    horas = 24
    if bisiesto:
        dias = 366

    try:
        #Mostramos en el log el inicio de la realizacion de la tarea
        logging.info(" --- COMIENZO PROCESO OBTENCION DE LOS COEFICIENTES DE REPARTO CE " + str(id_EnergyCommunity) + "--- ")

        #Paso 0: Parametros generales de la simulacion
        agenteEjecucionMySql = agente
        parametrosSimulacion = []
                
        #Si no existen simulaciones pendientes, entonces acabamos.
        parametrosSimulacion = ComunidadesEnergeticasServicio.obtenerParametrosEjecucionSimulacion(agenteEjecucionMySql,id_EnergyCommunity,Anyo)
        
        if parametrosSimulacion!= None:
          if len(parametrosSimulacion)==5:
            idEnergyCommunityProcess = parametrosSimulacion[0]
            idEnergyCommunity = parametrosSimulacion[1] 
            simulacion_fcDesde = parametrosSimulacion[2] #"2021-01-01 00:00:00"
            simulacion_fcHasta = parametrosSimulacion[3] #"2021-12-31 23:59:59"
            fcStart = parametrosSimulacion[4]
          else:
            idEnergyCommunityProcess = ""
            idEnergyCommunity = ""
            simulacion_fcDesde = "" #"2021-01-01 00:00:00"
            simulacion_fcHasta = "" #"2021-12-31 23:59:59"
            fcStart = ""
        else:
            logging.debug("ERROR en la CE " + str(id_EnergyCommunity) + " en el Paso 4.0, Fallo en el inicio del proceso")
            proceso = False

            return proceso, None

        #Realizamos la consulta para recuperar los parámetros de la ejecucion
        if (len(idEnergyCommunityProcess) != 0 and len(idEnergyCommunity) != 0 and len(simulacion_fcDesde) != 0 and len(simulacion_fcHasta) != 0):
            #Paso 1: Recupeamos e inicializamos las instancias con los datos recuperados de base de datos
            try:
                comunidadEnergetica = ComunidadesEnergeticasServicio.obtenerDatosComunidadEnergeticaDesdeBBDD(agenteEjecucionMySql, str(id_EnergyCommunity), simulacion_fcDesde, simulacion_fcHasta, Dias=dias, Horas=horas)
            except Exception as e:
                logging.debug("ERROR EN " + str(id_EnergyCommunity) + " PASO 4.1 DE OBTENCION DE DATOS DE LA BD: ", exc_info=True)
                proceso = False

                final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                return proceso, None
            
            #Paso 2: Ejecutamos los cálculos para el cumplimiento de las condiciones establecidas
            if proceso:
                try:
                    comunidadEnergetica.variacionObtencionCoef()
                except Exception as e:
                    logging.debug("ERROR EN " + str(id_EnergyCommunity) + " EN EL CALCULO DE COEFICIENTES DE REPARTO DEL PASO 4.2: ", exc_info=True)
                    proceso = False
                    final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)

                    return proceso, comunidadEnergetica
            else: 
                logging.debug("EN LA CE " + str(id_EnergyCommunity) + " El proceso se ha parado en el PASO 4.2")
                proceso = False
                final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                return proceso, None

            #Paso 3: Estimamos el reparto de la energía y lo imprimimos
            if proceso:
                try:
                    comunidadEnergetica.obtenerPrevisionEnergiaAsignadaByCoeficientesReparto()
                except Exception as e:
                    logging.debug("ERROR EN " + str(id_EnergyCommunity) + " EN EL REPARTO ENERGETICO DEL PASO 4.3: ", exc_info=True)
                    proceso = False
                    final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                    return proceso, comunidadEnergetica
            else: 
                logging.debug("EN " + str(id_EnergyCommunity) + " El proceso se ha parado en el PASO 4.3")
                proceso = False
                final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                return proceso, None

            #Paso 4: Calculamos los excedentes para cada cliente (en el caso de que los haya)
            if proceso:
                try:
                    comunidadEnergetica.obtenerPrevisionExcedenteAsignadoByCoeficientesReparto()
                except Exception as e:
                    logging.debug("ERROR EN " + str(id_EnergyCommunity) + " EN EL CALCULO DE EXCEDENTES PASO 4.4: ", exc_info=True)
                    proceso = False
                    final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                    return proceso, comunidadEnergetica
            else: 
                logging.debug("EN " + str(id_EnergyCommunity) + " El proceso se ha parado en el PASO 4.4")
                proceso = False
                final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                return proceso, None

            #Paso 5: Coeficiente de participacion
            if proceso:
                try:
                    comunidadEnergetica.obtenerCuotaUtilizacionUsuariosComunidadEnergetica()
                except Exception as e:
                    logging.debug("ERROR EN " + str(id_EnergyCommunity) + " EN LA CUOTA DE UTILIZACION PASO 4.5: ", exc_info=True)
                    proceso = False
                    final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                    return proceso, comunidadEnergetica
            else: 
                logging.debug("EN " + str(id_EnergyCommunity) + " El proceso se ha parado en el PASO 4.5")
                proceso = False
                final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                return proceso, None

            #Paso 6:  Borrado de info previa y Almacenamiento de los datos registrados (almacenamos en la tabla correspondiente los datos obtenidos).
            if proceso:
                try:
                    ComunidadesEnergeticasServicio.eliminarDatosUsuarios(agenteEjecucionMySql,comunidadEnergetica)
                    proceso = ComunidadesEnergeticasServicio.almacenarDatosCalculadosComunidadEnergetica(agenteEjecucionMySql, comunidadEnergetica)
                except Exception as e:
                    logging.error("ERROR EN " + str(id_EnergyCommunity) + " EN EL ALMACENAJE DE LOS DATOS EN BD PASO 4.6: ", exc_info=True)
                    proceso = False
                    final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                    return proceso, None
            else: 
                logging.error("EN " + str(id_EnergyCommunity) + " El proceso se ha parado en el PASO 4.6")
                proceso = False
                final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
                return proceso, None
                
            #Paso 7: Establecemos en base de datos como finalizado la ejecucion en la correspondiente tabla
            if proceso:
                final1000(agenteEjecucionMySql,fcStart,idEnergyCommunity)
            
            #Mostramos en el log el fin de la realizacion de la tarea
            logging.info(" - Task: CaracterizacionComunidadesEnergeticasTask: -> End exec. (" + tiem.now().__format__('%d/%m/%Y %H:%M:%S') + ") ")
            #Damos por finalizado el programa

            return proceso, comunidadEnergetica
        else:
            logging.warning("Paso 4 Calculo de coeficientes de reparto: Datos vacios (" + tiem.now().__format__('%d/%m/%Y %H:%M:%S') + ") ")
            final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)

            proceso = False
            return proceso, None

    except Exception as e:
        logging.error("EN " + str(id_EnergyCommunity) + " ERROR EN LA EJECUCUCIoN DEL PROCESO DEL PASO 4: ", exc_info=True)
        final1001(agenteEjecucionMySql,fcStart,idEnergyCommunity)
        proceso = False
        
        return proceso, None
    
if __name__ == "__main__":
    path = os.getcwd()
    direc = os.path.join(path,"logs")
    if not os.path.exists(direc):
        try:
            os.mkdir(direc)
        except Exception as e:
            direc = path
    
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[RotatingFileHandler(os.path.join(direc,'LEADING_PASO4_Output.log'), maxBytes=1000000, backupCount=4)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')

    #Paso 0: Parametros generales de la simulacion
    #Obtenemos el agente de base de datos que utilizaremos durante toda la ejecucion
    agenteEjecucionMySql = aB.Agente_MySql()
    # Obtenemos el anyo actual

    currentDateTime = tiem.now()
    date_year = currentDateTime.date()
    anyoDatosGuardarComunidad = date_year.strftime("%Y")
    
    # Condicion de anyo bisiesto: el resto tiene que ser 0
    
    resto = int(anyoDatosGuardarComunidad) % 4
    bisiesto = False
    if resto == 0:
        bisiesto = True

    ids_Comunidades = ComunidadesEnergeticasServicio.compruebaSiEjecutar(agenteEjecucionMySql)
    for ids in ids_Comunidades:
        try:
            Paso4(agenteEjecucionMySql,anyoDatosGuardarComunidad,ids, bisiesto)
        except Exception as e:
            logging.error("Fallo Paso 4: ", exc_info=True)
    
    agenteEjecucionMySql.cursor.close()