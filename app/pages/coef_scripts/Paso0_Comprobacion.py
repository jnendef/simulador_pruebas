# 
# Paso para la estimacion de la produccion de los generadores
# 
# @referencia fgregorio
# 
# @modificaciones jnaveiro
# 
from datetime import datetime as tiem

import pages.coef_scripts.agente_Basico as aB

import os

import logging
from logging.handlers import RotatingFileHandler

# Variables globales
HORAS = 24

### ---- METODO PARA OBTENCION DE INFORMACION DE INICIO ---

def obtInfoInicio(agente):
    sentenciaObtenerIdComunidad = "SELECT * FROM leading_db.energy_community_process a WHERE ((a.event_id = 0) OR (a.event_id = 10 AND a.result =1001)) AND a.start = (SELECT max(b.start) FROM energy_community_process b WHERE a.id_energy_community = b.id_energy_community);"

    records = agente.ejecutar(sentenciaObtenerIdComunidad)
    return records

# Funcion de comprobacion de comunidad energetica
def comprobacionCE(agente,datos):
    sentenciaColumnasCE = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'leading_db' AND TABLE_NAME = " + "'energy_community'" + ";"

    columnasCE = agente.ejecutar(sentenciaColumnasCE)

    sentenciaComprobacionCE = "SELECT * FROM leading_db.energy_community WHERE id_energy_community = " + str(datos["id_energy_community"]) + ";"

    records = agente.ejecutar(sentenciaComprobacionCE)

    datosCE = {}
    if any(records) and (len(records[0]) == len(columnasCE)):
        for i,j in zip(columnasCE,records[0]):
            datosCE[i[0]] = j
    else:
        # # logging.warning("Falta informacion en la tabla leading_db.energy_community")
        return False,datosCE

    if datosCE['name'] == "":
        # # logging.warning("Falta el nombre de la comunidad energetica")
        return False,datosCE
    
    if datosCE['location'] == "":
        # # logging.warning("Falta la localizacion de la comunidad energetica")
        return False,datosCE
    
    try:
        if float(datosCE['inst_cost']) <= 0.0:
            # # logging.warning("Falta especificar el coste de la instalacion") 
            return False,datosCE
    except:
        # # logging.warning("No se pudo convertir el coste a cifra")
        return False,datosCE
    
    try:
        if float(datosCE['inst_monthly_fee']) <= 0.0:
            # # logging.warning("Falta especificar el valor de la amortizacion de la instalacion") 
            return False,datosCE
    except:
        # # logging.warning("No se pudo convertir la amortizacion en cifra")
        return False,datosCE
    
    if datosCE['id_administrator'] == "":
        # # logging.warning("Falta el identificador del administrador")
        return False,datosCE

    try:
        if float(datosCE['max_participation']) < 0.0 or float(datosCE['max_participation']) > 100.0:
            # logging.warning("Fallo en la participacion maxima, no esta en el rango")
            return False,datosCE
    except:
        # logging.warning("No se pudo convertir la participacion maxima de la comunidad en cifra")
        return False,datosCE

    try:
        if float(datosCE['min_participation']) < 0.0 or float(datosCE['min_participation']) > 100.0:
            # logging.warning("Fallo en la participacion minima, no esta en el rango")
            return False,datosCE
    except:
        # logging.warning("No se pudo convertir la participacion minima de la comunidad en cifra")
        return False,datosCE
    
    try:
        if float(datosCE['energy_poverty']) < 0.0 or float(datosCE['energy_poverty']) > 100.0:
            # logging.warning("Fallo en la pobreza energetica, no esta en el rango")
            return False,datosCE
    except:
        # logging.warning("No se pudo convertir la participacion de pobreza energetica de la comunidad en cifra")
        return False,datosCE
    # El campo 'simulation_type' no está definido correctamente en la documentacion. Existe el campo pero no queda claro que tenga utilidad 
    return True,datosCE

# Funcion de comprobacion de usuarios de la comunidad energetica
def comprobacionUS(agente,datos):
    sentenciaColumnaUs = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'leading_db' AND TABLE_NAME = " + "'energy_community_consumer_profile'" + ";"

    columnasCE = agente.ejecutar(sentenciaColumnaUs)

    sentenciaComprobacionUs = "SELECT * FROM leading_db.energy_community_consumer_profile WHERE id_energy_community = " + str(datos["id_energy_community"]) + ";"

    records = agente.ejecutar(sentenciaComprobacionUs)

    datosUs = []
    if any(records) and (len(records[0]) == len(columnasCE)):
        for rc in records:
            aux = {}
            for i,j in zip(columnasCE,rc):
                aux[i[0]] = j
            datosUs.append(aux)
    else:
        # logging.warning("Falta informacion en la tabla leading_db.energy_community_consumer_profile")
        return False,datosUs
    
    for d in datosUs:
        try:
            if int(d['id_energy_community_consumer_profile']) <= 0:
                # logging.warning("Falta el dato incremental del identificador del perfil de consumo") 
                return False,datosUs
        except:
            # logging.error("No se pudo convertir el id_energy_community_consumer_profile a cifra")
            return False,datosUs
        
        try:
            if int(d['id_consumer_profile']) <= 0:
                # logging.warning("Falta el dato incremental del identificador del perfil") 
                return False,datosUs
        except:
            # logging.error("No se pudo convertir el id_consumer_profile a cifra")
            return False,datosUs
    
    return True,datosUs

# Funcion de comprobacion de generadores
def comprobacionGen(agente,datos):
    sentenciaColumnasFV = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'leading_db' AND TABLE_NAME = " + "'generator'" + ";"

    columnasFV = agente.ejecutar(sentenciaColumnasFV)

    sentenciaComprobacionCE = "SELECT * FROM leading_db.generator WHERE id_energy_community = " + str(datos["id_energy_community"]) + ";"

    records = agente.ejecutar(sentenciaComprobacionCE)
    datosFV = []
    if any(records) and (len(records[0]) == len(columnasFV)):
        for rc in records:
            aux = {}
            for i,j in zip(columnasFV,rc):
                aux[i[0]] = j
            datosFV.append(aux)
    else:
        # logging.warning("Falta informacion en la tabla leading_db.generator")
        return False,datosFV
    
    contenido = ['id_energy_community','id_generator_type','description','latitude','longitude','pv_module_type','pv_num_modules','pv_peak_power','pv_module_orientation','pv_module_tilt','wind_peak_power']

    for d in datosFV:
        for i in contenido:
            if str(d[i]) == "":
                # logging.debug("Fallo en la " + i + ", no esta en la tabla")
                return False,datosFV

    return True, datosFV

# Funcion de comprobacion de generadores
def comprobacionBat(agente,datos):
    sentenciaColumnasBat = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'leading_db' AND TABLE_NAME = " + "'storage_system'" + ";"

    columnasBat = agente.ejecutar(sentenciaColumnasBat)

    sentenciaComprobacionBat = "SELECT * FROM leading_db.storage_system WHERE id_energy_community = " + str(datos["id_energy_community"]) + ";"

    records = agente.ejecutar(sentenciaComprobacionBat)
    datosBat = []
    if any(records) and (len(records[0]) == len(columnasBat)):
        for rc in records:
            aux = {}
            for i,j in zip(columnasBat,rc):
                aux[i[0]] = j
            datosBat.append(aux)
    else:
        # logging.warning("Falta informacion en la tabla leading_db.storage_system")
        return False,datosBat
    
    contenido = ['id_energy_community', 'id_battery_type', 'ds_storage_system', 'voltage', 'nominal_capacity', 'max_limit', 'min_limit', 'init_capacity', 'max_hour_discharge']

    for d in datosBat:
        for i in contenido:
            if str(d[i]) == "":
                # logging.debug("Fallo en la " + i + ", no esta en la tabla")
                return False,datosBat

    return True, datosBat

# Funcion de comprobacion de que los datos estan
def comprobacionDb(agente,records):
    datosCe = {}
    datosGen = {}
    datosBat = {}
    datosUs = {}
    if len(records)>0:
        datos={}
        datos["id_energy_community_process"] = records[0]
        datos["id_energy_community"] = records[1]
        datos["event_id"] = records[2]
        datos["start"] = records[3]

        ce,datosCe = comprobacionCE(agente,datos)
        us,datosUs = comprobacionUS(agente,datos)
        gen,datosGen = comprobacionGen(agente,datos)
        bat,datosBat = comprobacionBat(agente,datos)
    else:
        # logging.info("No hay comunidades energeticas que simular")
        return False,datos,datosUs,datosCe,datosGen,datosBat
    
    if ce and us and gen:
        return True,datos,datosUs,datosCe,datosGen,datosBat
    else:
        return False,datos,datosUs,datosCe,datosGen,datosBat


#Inicio del programa principal para la deteccion de ausencias en la base de datos
if __name__ == "__main__":
    path = os.getcwd()
    direc = os.path.join(path,"logs\\LEADING_PASO0_Output.log")
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[RotatingFileHandler(direc, maxBytes=1000000, backupCount=4)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')

    #Paso 0: Parametros generales de la simulación
    #Obtenemos el agente de base de datos que utilizaremos durante toda la ejecución
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
    
    records = obtInfoInicio(agenteEjecucionMySql)

    for rc in records:
        okey,datos,datosUs,datosCe,datosGen,datosBat = comprobacionDb(agenteEjecucionMySql,rc)
        if not okey:
            print("Error, mire los logs")
            # logging.warning("Algo fue mal en la comunidad: "+str(rc[1]))
        else:
            print("Todo en orden")

    agenteEjecucionMySql.cursor.close()