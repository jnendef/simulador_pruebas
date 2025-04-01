# 
# Paso para el calculo del uso de la batería
# 
# @referencia fgregorio
# 
# @modificaciones jnaveiro
# 

import datetime
from datetime import timedelta
import os

import pages.coef_scripts.agente_Basico as aB

import logging
from logging.handlers import RotatingFileHandler

# Metodo para finalizar el proceso

def final1000(agente,fcStart,idComunidad):
    
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S') 
    sentenciaUpdate = "UPDATE leading_db.energy_community_process"
    sentenciaUpdate = sentenciaUpdate+ " SET stop = '" + now + "',"
    sentenciaUpdate = sentenciaUpdate+ " result = 1000 "
    sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 35 AND start='"+ fcStart + "'"
    agente.ejecutar(sentenciaUpdate)
    agente.commitTransaction()

    return

def final1001(agente,fcStart,idComunidad):
    # Actulizamos la entrada correspondiente al proceso
        
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S') 
    sentenciaUpdate = "UPDATE leading_db.energy_community_process"
    sentenciaUpdate = sentenciaUpdate+ " SET stop = '" + now + "',"
    sentenciaUpdate = sentenciaUpdate+ " result = 1001 "
    sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 35 AND start='"+ fcStart + "';"
    agente.ejecutar(sentenciaUpdate)
    agente.commitTransaction()
    
    return

# Funcion que comprueba si hay comunidades pendientes de simulacion 
def compruebaSiEjecutar(agenteEjecucionMySql):
    # Por cada usuario cargamos su lista de consumos
    # Consultamos si nos toca ejecutar
    sqlCommunityProcess = "SELECT * FROM leading_db.energy_community_process a WHERE ((a.event_id = 30 AND a.result=1000) OR (a.event_id = 35 AND a.result =1001)) AND a.start = (SELECT max(b.start) FROM leading_db.energy_community_process b WHERE a.id_energy_community = b.id_energy_community)"

    rs_communityProcess = agenteEjecucionMySql.ejecutar(sqlCommunityProcess)

    vector_idEnergyCommunity = []

    for rs in rs_communityProcess:
        vector_idEnergyCommunity.append(int(rs[1]))

    return vector_idEnergyCommunity

### ---- METODO PARA OBTENER EL BALANCE DE ENERGIA EN CADA HORA ----

def balancehorario (generacionTotal, consumoTotal, capacidadDisponibleAnterior,limite_capacidad_maxima,limite_capacidad_minima):
    # --------------------------------------------------------------------------
    # Diseño del Algoritmo
    # --------------------------------------------------------------------------

    # Parámetros de entrada

    # Carga inicial de la batería (Q0)     Carga máxima de la batería (Qmax)     Carga mínima de la batería (Qmin)

    # Variables

    # Carga aportada por la bateria (Qaportada)
    # Carga sobrante en batería (Qsob)
    # Generación total: fotovoltaica + eólica (G)
    # Consumo total (C)

    # 1.- Comparamos la generación total en una hora (Gi) con el consumo total en esa hora (Ci)

    #          1.1- Si Gi >= Ci:

    #                 * Qaportada(i) = 0
    #                 * Qsob(i)=Qsob(i-1)+Gi-Ci
    #                   - Si Qsob(i) > Qmax --> Qsob(i)=Qmax & Eexp=Qsob(i)-Qmax & Eimp=0
    #                   - Si Qsob(i) <= Qmax --> Qsob(i)=Qsob(i) & Eexp=0 & Eimp=0

    #          1.2- Si Gi < Ci:

    #               1.2.1- Si Ci-Gi < Qsob(i-1)-Qmin:
    #                       * Qaportada(i) = Ci-Gi
    #                       * Qsob(i)=Qsob(i-1)-Qaportada(i)
    #                       * Eexp=0 & Eimp=0

    #               1.2.2- Si Ci-Gi >= Qsob(i-1)-Qmin:
    #                       * Qaportada(i) = Qsob(i-1)-Qmin
    #                       * Qsob(i)=Qmin
    #                       * Eexp=0 & Eimp=Ci-Gi-Qaportada(i)

    if(generacionTotal>= consumoTotal): 
        #Generación mayor que consumo
        capacidadAportada = 0
        capacidadDisponible = capacidadDisponibleAnterior + generacionTotal - consumoTotal
        if( capacidadDisponible > limite_capacidad_maxima): 
            # Si la capacidad disponible excede el limite superior, nos quedamos con el limite superior
            energiaExportada = capacidadDisponible - limite_capacidad_maxima
            capacidadDisponible = limite_capacidad_maxima
            energiaImportada = 0
        else:
            energiaExportada = 0
            energiaImportada = 0
                  
    else: # Consumo mayor que generación
        if ((consumoTotal - generacionTotal) < (capacidadDisponibleAnterior - limite_capacidad_minima)):  # Si la energía puede salir de las baterias sin sobrepasar el límite inferior
            capacidadAportada = consumoTotal - generacionTotal
            capacidadDisponible = capacidadDisponibleAnterior - capacidadAportada
            energiaExportada = 0
            energiaImportada = 0
        else:
            capacidadAportada = capacidadDisponibleAnterior - limite_capacidad_minima
            capacidadDisponible = limite_capacidad_minima
            energiaExportada = 0
            energiaImportada = consumoTotal - generacionTotal - capacidadAportada

                    
    # El balance siempre, independientemente del caso, será la capacidad disponible anterior menos la capacidad disponible
    balance = capacidadDisponibleAnterior - capacidadDisponible
    
    return (balance, capacidadDisponible, capacidadAportada, energiaExportada, energiaImportada)


### ---- BLOQUE PRINCIPAL DEL PROGRAMA ----    

def Paso3(agente, idComunidad):
    """
    Definicion: Esta funcion es la principal de ejecucion del proceso de cálculo de gestion de las baterias. 
    
    Variables de entrada: agente, idComunidad
    
    Variables de salida: proceso,  VectorDatosBaterias
    
    Objetos relevantes:
    
        1. agenteEjecucionMySql
    
    Librerías que se llaman:

        1. agente_Basico
        2. datetime
        3. logging
    """

    proceso =True
    VectorDatosBaterias = []

    try:
        # logging.info (" --- SCRIPT SIMULACION COMPORTAMIENTO BATERIA COMUNIDAD ENERGÉTICA CE " + str(idComunidad) + " --- ")
        # Establemos en el energy_community_process la fecha de comienzo

        fcStart = datetime.datetime.now()
        fcStart = fcStart.strftime('%Y-%m-%d %H:%M:%S') 
        sentenciaInsertNuevoRegistroProcess = "INSERT INTO leading_db.energy_community_process  (id_energy_community, event_id, start) VALUES ( "
        sentenciaInsertNuevoRegistroProcess = sentenciaInsertNuevoRegistroProcess + str (idComunidad) + ", 35, '" + fcStart + "') "
        agente.ejecutar(sentenciaInsertNuevoRegistroProcess)
        agente.commitTransaction()

        # Recuperamos los datos del sistema de almacenamiento correspondiente a esta comunidad

        sentenciaObtenerParametrosAlmacenamiento = "SELECT * FROM leading_db.storage_system WHERE id_energy_community = '" + str(idComunidad) + "';"    

        ParametrosAlmacenamiento = agente.ejecutar(sentenciaObtenerParametrosAlmacenamiento)

        if (len(ParametrosAlmacenamiento)==0):
            final1000(agente,fcStart,idComunidad)
            return proceso, VectorDatosBaterias


        id_storage_system = str(ParametrosAlmacenamiento[0][0])    
        limite_capacidad_maxima = float(ParametrosAlmacenamiento[0][6]); #kWh
        limite_capacidad_minima = float(ParametrosAlmacenamiento[0][7]); #kWh
        cargaInicialBateria = float(ParametrosAlmacenamiento[0][8]); #kWh

        # Paso 2: Recuperamos de la base de datos los consumos totales y la generacion total de     la comunidad

        # Paso 2.1.- Recuperamos un vector con todos las generaciones del año

        # Consulta para recuperar la generacion total de la comunidad

        sql_aeileading_total_generation_community = """
        SELECT EC.ID_ENERGY_COMMUNITY, generator_data.timestamp, SUM(generator_data.production)
        FROM energy_community AS EC
        INNER JOIN generator AS generator_community ON generator_community.id_energy_community =    EC.id_energy_community
        INNER JOIN generator_data AS generator_data ON generator_data.id_generator =    generator_community.id_generator
        WHERE EC.ID_ENERGY_COMMUNITY = '""" + str(idComunidad) + """' 
        GROUP BY EC.ID_ENERGY_COMMUNITY, generator_data.timestamp;
        """

        # Ejecutamos la consulta
        registrosDatosGeneracionComunidad = agente.ejecutar (sql_aeileading_total_generation_community)

        # Paso 2.2.- Recuperamos un vector con todos los consumos del año

        # Consulta para recuperar el consumo total de la comunidad
        sql_aeileading_current_consumption_community = """
        SELECT EC.ID_ENERGY_COMMUNITY, user_data.timestamp, SUM(user_data.consumption)
        FROM energy_community AS EC
        INNER JOIN user AS user_community ON user_community.id_energy_community = EC.   id_energy_community
        INNER JOIN user_data AS user_data ON user_data.id_user = user_community.id_user
        WHERE EC.ID_ENERGY_COMMUNITY = '""" + str(idComunidad) + """' 
        GROUP BY EC.ID_ENERGY_COMMUNITY, user_data.timestamp;
        """

        # Ejecutamos la consulta
        registrosDatosConsumosComunidad = agente.ejecutar(sql_aeileading_current_consumption_community)

        # Paso 2.3.- Deben coincidir el número de horas de generación y consumos
        if(len(registrosDatosConsumosComunidad)!=len(registrosDatosGeneracionComunidad)):
            # logging.info("ERROR EN EL PASO 3: No coincide el número de registros de generación respecto a los de consumo")

            return proceso,VectorDatosBaterias

        # Paso 3: Creamos una instancia con el estado inicial de la batería

        # Creo la tupla con el estado inicial de la bateria

        fecha0= registrosDatosGeneracionComunidad[0][1] - timedelta(hours=1)
        estadoBateria0 = (id_storage_system, fecha0, 0, 0, 0, cargaInicialBateria, 0, 0, 0)

        VectorDatosBaterias.append(estadoBateria0)

        # Paso 4: Creamos una instancia por cada iteración (desde la segunda hora hasta el final)

        for indice in range(len(registrosDatosGeneracionComunidad)):

            # Obtengo los datos para la hora
            horaDato = registrosDatosGeneracionComunidad[indice][1]
            horaDato = horaDato.strftime('%Y-%m-%d %H:%M:%S')
            generacionHora = registrosDatosGeneracionComunidad[indice][2]
            consumoHora = registrosDatosConsumosComunidad[indice][2]


            # Calculo el estado de la bateria en la hora
            estadoBateriaHora = balancehorario(float(generacionHora), float(consumoHora), float (VectorDatosBaterias[indice][5]),limite_capacidad_maxima,limite_capacidad_minima) 

            tuplaVectorDatosBaterias = (id_storage_system, horaDato, float(generacionHora), float(consumoHora), float(estadoBateriaHora[2]), float(estadoBateriaHora[1]), float (estadoBateriaHora[0]), float(estadoBateriaHora[3]), float(estadoBateriaHora[4]))

            VectorDatosBaterias.append(tuplaVectorDatosBaterias)

        #Paso 5: Imprimimos los resultados / Guardamos en base de datos

        # Guardamos los resultados en la base de datos
        sentenciaInsert = "INSERT INTO leading_db.storage_system_cycle_data (id_storage_system, timestamp, total_energy_generators, total_consumption, battery_energy_supplied, battery_energy_storaged, battery_energy_balance,  community_energy_exported, community_energy_imported) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        agente.ejecutarMuchos(sentenciaInsert, VectorDatosBaterias)
        agente.commitTransaction()

        # Paso 6: Indicamos que la ejecución ha acabado correctamente

        now = datetime.datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S') 
        sentenciaUpdate = "UPDATE leading_db.energy_community_process"
        sentenciaUpdate = sentenciaUpdate+ " SET stop = '" + now + "',"
        sentenciaUpdate = sentenciaUpdate+ " result = 1000 "
        sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + "   AND event_id = 35 AND start='"+ fcStart + "'"

        agente.ejecutar(sentenciaUpdate)
        agente.commitTransaction()

    # Si ocurre un error lo indicamos
    except Exception as ex:
        proceso = False
        # logging.error("ERROR EN EL PASO 3: EXCEPCION EN LA EJECUCION DEL PROCESO: ", exc_info=True)

        final1001(agente,fcStart,idComunidad)

    else:
        return proceso, VectorDatosBaterias

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
        handlers=[RotatingFileHandler(os.path.join(direc,'LEADING_PASO3_Output.log'), maxBytes=1000000, backupCount=4)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')

    #Paso 0: Parametros generales de la simulación
    #Obtenemos el agente de base de datos que utilizaremos durante toda la ejecución
    agenteEjecucionMySql = aB.Agente_MySql()
    # Obtenemos el anyo actual

    currentDateTime = datetime.datetime.now()
    date_year = currentDateTime.date()
    anyoDatosGuardarComunidad = date_year.strftime("%Y")
    
    # Condicion de anyo bisiesto: el resto tiene que ser 0
    
    resto = int(anyoDatosGuardarComunidad) % 4
    bisiesto = False
    if resto == 0:
        bisiesto = True

    ids_Comunidades = compruebaSiEjecutar(agenteEjecucionMySql)
    for ids in ids_Comunidades:
        try:
            Paso3(agenteEjecucionMySql,ids)
        except Exception as e:
            pass
            # logging.error("Fallo Paso 3: " , exc_info=True)
    
    agenteEjecucionMySql.cursor.close()