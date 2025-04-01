# 
# Paso para la estimacion de la produccion de los generadores
# 
# @referencia fgregorio
# 
# @modificaciones jnaveiro
# 

import requests
import json
import os

import datetime
from datetime import date

import numpy as np
import pages.coef_scripts.agente_Basico as aB

import logging
from logging.handlers import RotatingFileHandler

# Variables globales
HORAS = 24

# Metodo para finalizar el proceso

def final1000(agente,fcStart,idComunidad):
    
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S') 
    sentenciaUpdate = "UPDATE leading_db.energy_community_process"
    sentenciaUpdate = sentenciaUpdate+ " SET stop = '" + now + "',"
    sentenciaUpdate = sentenciaUpdate+ " result = 1000 "
    sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 10 AND start='"+ fcStart + "'"
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
    sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 10 AND start='"+ fcStart + "';"
    agente.ejecutar(sentenciaUpdate)
    agente.commitTransaction()
    
    return

### ---- METODO PARA OBTENCION DE INFORMACION DE INICIO ---

def obtInfoInicio(agente):
    sentenciaObtenerIdComunidad = "SELECT * FROM leading_db.energy_community_process a WHERE ((a.event_id = 0) OR (a.event_id = 10 AND a.result =1001)) AND a.start = (SELECT max(b.start) FROM energy_community_process b WHERE a.id_energy_community = b.id_energy_community);"

    records = agente.ejecutar(sentenciaObtenerIdComunidad)
    return records

### ---- METODO PARA OBTENCION DE UNA CE ---

def obt_comunidad(agente, idComunidad):
    sentenciaObtenerIdComunidad = "SELECT * FROM leading_db.energy_community_process WHERE ((event_id = 0) OR (event_id = 10 AND result =1001)) AND id_energy_community = "+str(idComunidad)+";"

    records = agente.ejecutar(sentenciaObtenerIdComunidad)
    return records

### ---- METODO PARA CONVERTIR VIENTO EN POTENCIA ----       
    
def ConvierteVientoEnPotencia(VelocidadViento):
    # Esta funcion es valida para un generador de 3kW de potencia máxima
    # Formulas para la simulacion del aerogenerador a partir de la velocidad del viento
    if VelocidadViento < 2:
        PotenciaAerogenerador=0
    
    elif (VelocidadViento >= 2 and VelocidadViento < 12.5):
        PotenciaAerogenerador=-0.0235*VelocidadViento**6+0.7648*VelocidadViento**5-9.23*VelocidadViento**4+52.365*VelocidadViento**3-118.34*VelocidadViento**2+96.214*VelocidadViento-6.4851

    elif (VelocidadViento >= 12.5 and VelocidadViento < 16):
        PotenciaAerogenerador=11.446*VelocidadViento**3-520.07*VelocidadViento**2+7715.3*VelocidadViento-34178

    else:
        PotenciaAerogenerador=3000
    
    return (PotenciaAerogenerador/1000);  # Lo dividimos por 1000 para dar kW 

### ---- METODO PARA OBTENER DATOS DE PV ----

def obtenerDatosPVGIS_PV (pv_peakpower, pv_aspect, pv_angle, lat, lon, Dias):
    
    # Parametros fijos para la obtención de datos
    startyear="2011"
    endyear="2020"
    pvcalculation="1"
    loss="14"
    trackingtype="0"
    browser="0"
    outputformat="json"
    
    # Cuidado que cambio la url en septiembre del anyo 2024
    # jsonRequest = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?"
    jsonRequest = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc?"
    jsonRequest = jsonRequest + "lat=" + lat + "&"
    jsonRequest = jsonRequest + "lon=" + lon + "&"
    jsonRequest = jsonRequest + "startyear=" + startyear + "&"
    jsonRequest = jsonRequest + "endyear=" + endyear + "&"
    jsonRequest = jsonRequest + "pvcalculation=" + pvcalculation + "&"
    jsonRequest = jsonRequest + "peakpower=" + pv_peakpower + "&"
    jsonRequest = jsonRequest + "loss=" + loss + "&"
    jsonRequest = jsonRequest + "trackingtype=" + trackingtype + "&"
    jsonRequest = jsonRequest + "angle=" + pv_angle + "&"
    jsonRequest = jsonRequest + "aspect=" + pv_aspect + "&"
    jsonRequest = jsonRequest + "browser=" + browser + "&"
    jsonRequest = jsonRequest + "outputformat=" + outputformat
   
    # Componemos y ejecutamos la petición 
    requestResponse = requests.get(jsonRequest)
    
    # Creamos una matriz de 3 dimensiones para ir guardando los registros recuperados de la petición
    
    anyos = int(endyear)-int(startyear)+1
 
    matrizResultados = np.zeros((Dias,HORAS, anyos))

    # Procesado de la información. Obtener promedio por hora, para cada día de cada mes (numAños)
    
    # Obtenemos el código de respuesta de la petición 
    requestResponseStatus = requestResponse.status_code
    
    contAnyos = 0
    if requestResponseStatus==200:
    
        #  Manejamos la respuesta JSON
        json_data = json.loads(requestResponse.text)
    
        json_data_outputHourly = json_data["outputs"]["hourly"]
    
        # Variable para que coincida la estructura de datos en los años bisiestos
        decrementarBisiesto = False
       
        for itData in json_data_outputHourly:
        
            # Obtenemos las distintas variables de la petición
            it_time = itData["time"]
            it_year = it_time[0:4]
            it_month = it_time[4:6]
            it_day = it_time[6:8]
            it_hour = it_time[9:11]
                    
            it_energia = itData["P"]
    
            # Almacenamos en la matriz el valor obtenido
            # Obtenemos la primera dimension de nuestra matriz
            dateIT = date(int(it_year), int(it_month), int(it_day))
            dateStartYear = date(int(it_year), 1, 1)
            it_numDayInYear = (dateIT - dateStartYear).days
            
            # Almacenamos en la matriz de resultados el valor obtenido
            # FIXME: Ignoramos el 29/02 en años bisiestos para respetar la estructura de datos            
            if int(it_month)==2 and int(it_day)==29:
               decrementarBisiesto = True
               
            # Si iniciamos anyo limpiamos este flag para que no acumule retraso si no es bisiesto
            if int(it_month)==1 and int(it_day)==1:
               decrementarBisiesto = False
                   
            #FIXME: Si esto ocurre, el día 29 machaca el 28 y a partir de aqui normal
            if decrementarBisiesto:
                it_numDayInYear = it_numDayInYear -1
                  
            # Guardamos el dato axiliar obtenido
            matrizResultados [int(it_numDayInYear),int(it_hour),contAnyos] = float(it_energia) 
            contAnyos = int(it_year) - int(startyear)
        
        # Calculamos el valor promedio para cada hora y dia alcenado en la matriz auxiliar
    
        # Declaramos la matriz final con 2 dimensiones (dias y horas), donde vamos a almacenar el valor promedio
        # Y dividimos entre mil para obtener los kWh
        matrizEnergiaPromedio = matrizResultados.mean(2)/1000
        
        return matrizEnergiaPromedio

    else:
        return np.zeros((Dias,HORAS))


### ---- METODO PARA OBTENER DATOS DE EOLICA ----       
    
def obtenerDatosPVGIS_eolica (lat, lon, Dias):    
    
    #print("Método obtenerDatosPVGIS_PV");
    
    # Parametros fijos para la obtención de datos
    outputformat="json"

    # Cuidado que cambio la url en septiembre de 2024
    # jsonRequest = "https://re.jrc.ec.europa.eu/api/v5_2/tmy?"; #lo añado para usar el TMY
    jsonRequest = "https://re.jrc.ec.europa.eu/api/tmy?"; #lo añado para usar el TMY
    
    jsonRequest = jsonRequest + "lat=" + lat + "&"
    jsonRequest = jsonRequest + "lon=" + lon + "&"
    jsonRequest = jsonRequest + "outputformat=" + outputformat

    # Componemos y ejecutamos la petición
    requestResponse = requests.get(jsonRequest)
 
    # Creamos una matriz de 2 dimensiones para ir guardando los registros recuperados de la petición
    matrizResultados = np.zeros((Dias,HORAS))
  
    # Procesado de la información.
   
    # Obtenemos el código de respuesta de la petición
    requestResponseStatus = requestResponse.status_code
    
    #print("Codigo de la respuesta obtenido:");
    #print(requestResponseStatus);

    if requestResponseStatus==200:

        # Manejamos la respuesta JSON
        json_data = json.loads(requestResponse.text)
    
        json_data_outputHourly = json_data["outputs"]["tmy_hourly"] #tmy_hourly lo añado para usar el TMY

        # Variable para que coincida la estructura de datos en los años bisiestos
        decrementarBisiesto = False
       
        for itData in json_data_outputHourly:
            
            # Obtenemos las distintas variables de la petición
            it_time = itData["time(UTC)"] #time(UTC) lo añado para usar el TMY
            it_year = it_time[0:4]
            it_month = it_time[4:6]
            it_day = it_time[6:8]
            it_hour = it_time[9:11]
                    
            it_wind_speed = itData["WS10m"]
            

            # Almacenamos en la matriz el valor obtenido
            # Obtenemos la primera dimension de nuestra matriz
            dateIT = date(int(it_year), int(it_month), int(it_day))
            dateStartYear = date(int(it_year), 1, 1)
            it_numDayInYear = (dateIT - dateStartYear).days
            
            # Almacenamos en la matriz de resultados el valor obtenido
            # FIXME: Ignoramos el 29/02 en años bisiestos para respetar la estructura de datos            
            if int(it_month)==2 and int(it_day)==29:
               decrementarBisiesto = True
               
            # Si iniciamos anyo limpiamos este flag para que no acumule retraso si no es bisiesto
            if int(it_month)==1 and int(it_day)==1:
               decrementarBisiesto = False
               
            # FIXME: Si esto ocurre, el día 29 machaca el 28 y a partir de aqui normal
            if decrementarBisiesto:
                it_numDayInYear = it_numDayInYear -1
                

            # Guardamos el dato axiliar obtenido
            matrizResultados [int(it_numDayInYear),int(it_hour)] = ConvierteVientoEnPotencia(float(it_wind_speed))
        
        return matrizResultados
    
def generaciongeneral(anyoDatosGuardarComunidad,matrizEnergiaPromedio,VectorDatosProduccion,generator_id,dateIndex,contadorDias,dia):
    for hora in range(HORAS):
        # Obtenemos el valor
        valorPromedioDiaHora = matrizEnergiaPromedio [dia][hora]

        # Obtenemos la fecha para cada dato en función de la posición
        dateStartYear = date(int(anyoDatosGuardarComunidad), 1, 1)
        dateIndex = dateStartYear + datetime.timedelta(days=contadorDias)
        timestampInsert = str(dateIndex)
        timestampInsert = timestampInsert + " " + str(hora) + ":" + "00:00"

        # Formamos el vector con las tuplas de datos
        TuplaDatosProduccion = (str(generator_id), str(timestampInsert), str(valorPromedioDiaHora))
        VectorDatosProduccion.append(TuplaDatosProduccion)

    return VectorDatosProduccion

def generacionBisiesto(anyoDatosGuardarComunidad,matrizEnergiaPromedio,VectorDatosProduccion,generator_id,dateIndex,contadorDias,dia):
    for hora in range(HORAS):
        # Obtenemos el valor
        valorPromedioDiaHora = matrizEnergiaPromedio [dia][hora]

        # Obtenemos la fecha para cada dato en función de la posición
        dateStartYear = date(int(anyoDatosGuardarComunidad), 1, 1)
        dateIndex = dateStartYear + datetime.timedelta(days=contadorDias)
        timestampInsert = str(dateIndex)
        timestampInsert = timestampInsert + " " + str(hora) + ":" + "00:00"

        # Formamos el vector con las tuplas de datos
        TuplaDatosProduccion = (str(generator_id), str(timestampInsert), str(valorPromedioDiaHora))
        VectorDatosProduccion.append(TuplaDatosProduccion)
        
        if dateIndex.day == 28 and dateIndex.month == 2:
            dateIndexAux = dateStartYear + datetime.timedelta(days=(contadorDias+1))
            timestampauxInsert = str(dateIndexAux)
            timestampauxInsert = timestampauxInsert + " " + str(hora) + ":" + "00:00"

            # Formamos el vector con las tuplas de datos
            TuplaDatosProduccion = (str(generator_id), str(timestampauxInsert), str(valorPromedioDiaHora))
            VectorDatosProduccion.append(TuplaDatosProduccion)

    return VectorDatosProduccion


### ---- BLOQUE PRINCIPAL DEL PROGRAMA ----    

def Paso1(agente, records, anyoDatosGuardarComunidad, bisiesto):
    """
    Definicion: Esta funcion es la principal de ejecucion del proceso de Estimacion de la produccion. Se encarga, dentro del conjunto de scripts, de la obtención de la produccion FV y Eo mediante la simulacion de PVGIS y los datos de velocidad del viento para el calculo de produccion eolica. Una vez obtenidos, se envian a la base de datos. 
    
    Variables de entrada: agente, records, anyoDatosGuardarComunidad, bisiesto
    
    Variables de salida: proceso,  VectorDatosProduccion, idComunidad
    
    Objetos relevantes:
    
        1. agenteEjecucionMySql
    
    Librerías que se llaman:

        1. agente_Basico
        2. datetime
        3. logging
        4. requests
        5. json
    """
    Dias=365
    if bisiesto:
        Dias =366
    proceso = True
    idComunidad = -1
    VectorDatosProduccion = []

    # Establemos en el energy_community_process la fecha de comienzo
    fcStartD = datetime.datetime.now()
    fcStart = fcStartD.strftime('%Y-%m-%d %H:%M:%S')
    
    # Impresión del mensaje de bienvenida

    if(len(records)==0):
        # logging.info("Paso1 de Estimacion de la produccion: Sin comunidades que simular en este paso")
        return proceso, VectorDatosProduccion, idComunidad

    try:
        idComunidad = records[1]
        result = records[-1]

        # logging.info(" --- COMIENZO PROCESO OBTENCION ESTIMACION PRODUCCION A TRAVES API PVGIS CE " + str(idComunidad) + " --- ")

        if result == None:
            result = 1000
        else:
            result = int(result)

        if result == 1000:
            sentenciaInsertNuevoRegistroProcess = "INSERT INTO leading_db.energy_community_process (id_energy_community, event_id, start) VALUES ( "
            sentenciaInsertNuevoRegistroProcess = sentenciaInsertNuevoRegistroProcess + str(idComunidad) + ", 10, '" + fcStart + "') "
        else:
            now = datetime.datetime.now()
            now = now.strftime('%Y-%m-%d %H:%M:%S') 
            sentenciaInsertNuevoRegistroProcess = "UPDATE leading_db.energy_community_process" + " SET start = '" + now + "' WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 10 AND result = 1001;"
        
        agente.ejecutar(sentenciaInsertNuevoRegistroProcess)
        agente.commitTransaction()
        
        # Consulta para obtener los generadores de la comunidad (de cualquier tipo)
        sql = "SELECT id_generator, id_generator_type, pv_peak_power, pv_module_orientation, pv_module_tilt, latitude, longitude, wind_peak_power  FROM leading_db.generator where id_energy_community = " + str(idComunidad)
        
        rowDataGeneradores = agente.ejecutar(sql)
        
        if(len(rowDataGeneradores)==0):
            # logging.info("Paso1 de Estimacion de la produccion: Sin generadores que simular en este paso")
            return proceso, VectorDatosProduccion, idComunidad
            
        # Para cada generador de la comunidad
        for rowGenerador in rowDataGeneradores:
        
            # Obtenemos todos los datos del generador
            generator_id = str(rowGenerador[0])
            generator_type = str(rowGenerador[1])
            pv_peakpower = str(rowGenerador[2])
            pv_aspect = str(rowGenerador[3])
            pv_angle = str(rowGenerador[4])
            lat = str(rowGenerador[5])
            lon = str(rowGenerador[6])
            wind_peak_power = str(rowGenerador[7])

            # --- En función del tipo de generador, llamamos a una u otra función de PVGIS (PV, EOLICO) ---
            
            if generator_type == '1':
            
                # Cálculo para el tipo de generador FV (generator_type = 1)
                matrizEnergiaPromedio = obtenerDatosPVGIS_PV (pv_peakpower, pv_aspect, pv_angle, lat, lon, Dias)

            elif generator_type == '2':
                try:
                    wind_peak_power = float(wind_peak_power)
                except:
                    # logging.debug("El dato de potencia eolica se ha puesto en 1.")
                    wind_peak_power = 1.0
                # Cálculo para el tipo de generador eolico (generator_type = 2)            
                matrizEnergiaPromedio = wind_peak_power*obtenerDatosPVGIS_eolica (lat, lon, Dias)

            # Almacenamiento en la base de datos. Componemos el insert y lo ejecutamos
            try:
                # Creamos el vector donde meteremos las tuplas de datos antes de hacer el insert en la base de datos
                # Obtenemos la fecha para cada dato en función de la posición
                dateStartYear = date(int(anyoDatosGuardarComunidad), 1, 1)
                contadorDias = 0
                for dia in range(Dias):
                    # Si el año es bisiesto, duplicamos los datos del día 28/02 y los guardamos como si fueran del 29/02
                    dateIndex = dateStartYear + datetime.timedelta(days=contadorDias)
                    if dateIndex.day == 29 and dateIndex.month==2:
                        pass
                    else:
                        if bisiesto:
                            VectorDatosProduccion = generacionBisiesto(anyoDatosGuardarComunidad,matrizEnergiaPromedio,VectorDatosProduccion,generator_id,dateIndex,contadorDias,dia)
                        else:
                            VectorDatosProduccion = generaciongeneral(anyoDatosGuardarComunidad,matrizEnergiaPromedio,VectorDatosProduccion,generator_id,dateIndex,contadorDias,dia)
                    contadorDias += 1
                
            except Exception as e:
                proceso = False
                # logging.error("ERROR EN EL PASO 1: EXCEPCION EN LA OPERACION DE BASE DE DATOS, ", exc_info=True)
                final1001(agente, fcStart, idComunidad)

                return proceso, VectorDatosProduccion, idComunidad

            try:
                # Ejecutamos el insert en base de datos para todos los datos de los generadores que están almacenados en el vector de datos a insertar
                sentenciaDelete = "DELETE FROM leading_db.generator_data WHERE id_generator = " + str(generator_id) + ";"
                agente.ejecutar(sentenciaDelete)
                agente.commitTransaction()
            except Exception as e:
                pass
                # logging.info("FALLO EN EL BORRADO EN LA BASE DE DATOS EN EL PASO 1: ", exc_info=True)

        if proceso:
            try:
                sentenciaInsert = "INSERT INTO leading_db.generator_data (id_generator, timestamp, production) VALUES (%s, %s, %s);"
                agente.ejecutarMuchos(sentenciaInsert, VectorDatosProduccion)
                agente.commitTransaction()
            except Exception as e:
                pass
                # logging.error("ERROR EN INSERCION DE MUCHOS EN BASE DE DATOS EN EL PASO 1: ", exc_info=True)

        # Indicamos que la ejecución ha acabado correctamente   
        final1000(agente,fcStart,idComunidad)

    # Si ocurre un error lo indicamos
    except Exception as e:
        proceso = False
        # logging.error("ERROR EN EL PASO 1: EXCEPCION EN LA EJECUCION DEL PROCESO: ", exc_info=True)

        final1001(agente, fcStart, idComunidad)

    else:
        return proceso, VectorDatosProduccion, idComunidad

if __name__ == "__main__":
    path = os.getcwd()
    direc = os.path.join(path,"logs")
    if not os.path.exists(direc):
        try:
            os.mkdir(direc)
        except Exception as e:
            direc = path
    
    logging.basicConfig(
        level= logging.DEBUG,
        handlers=[RotatingFileHandler(os.path.join(direc,'LEADING_PASO1_Output.log'), maxBytes=1000000, backupCount=4)],
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
    
    records = obtInfoInicio(agenteEjecucionMySql)
    # records = obt_comunidad(agenteEjecucionMySql,202)

    for rc in records:
        try:
            Paso1(agenteEjecucionMySql, rc, anyoDatosGuardarComunidad, bisiesto)
        except Exception as e:
            # logging.debug("Fallo Paso 1: ", exc_info=True)
            pass

    agenteEjecucionMySql.cursor.close()