from pages.coef_scripts.agente_Basico import Agente_MySql
import streamlit as st
import logging
# import pandas as pd

# Envio de la informacion de la comunidad
def envioComu(agente,comunidad):
    sentenciaEnvio = " INSERT INTO leading_db.energy_community (name, location, inst_cost, inst_finance, inst_monthly_fee, id_administrator,energy_produced, max_participation,min_participation,energy_poverty,simulation_type) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s);"
    tupla = (comunidad['name'],comunidad['location'],comunidad['inst_cost'], 0, comunidad['inst_monthly_fee'],5,0.00,comunidad['max_participation'],comunidad['min_participation'],comunidad['energy_poverty'],2)
    agente.ejecutarMuchos(sentenciaEnvio,[tupla])
    idComunidad = agente.cursor.lastrowid
    return idComunidad

# Envio de la informacion de los generadores
def envioGen(agente,generador,idComunidad,tipo):
    lista = []
    if tipo == 1:
        sentenciaEnvio = " INSERT INTO leading_db.generator (id_energy_community, id_generator_type, description, latitude, longitude, pv_num_modules,pv_peak_power,pv_module_type,pv_module_orientation,pv_module_tilt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        for i in generador:
            tupla = (idComunidad,1,i["description"],i["latitude"],i["longitude"],i["pv_num_modules"],i["pv_peak_power"],i["pv_module_type"],i["pv_module_orientation"],i["pv_module_tilt"])
            lista.append(tupla)
    else:
         sentenciaEnvio = " INSERT INTO leading_db.generator (id_energy_community, id_generator_type, description, latitude, longitude, wind_peak_power) VALUES (%s, %s, %s, %s, %s, %s);"
         for i in generador:
            tupla = (idComunidad,2,i["description"],i["latitude"],i["longitude"],i["wind_peak_power"])
            lista.append(tupla)
    
    agente.ejecutarMuchos(sentenciaEnvio,lista)

    return

# Envio de la informacion de las baterias
def envioBat(agente,idComunidad, baterias):
    sentenciaEnvio = " INSERT INTO leading_db.storage_system (id_energy_community, id_battery_type, ds_storage_system, voltage, nominal_capacity, max_limit,min_limit,init_capacity,max_hour_discharge) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"

    lista = []
    for i in baterias:
        tupla = (idComunidad,i["id_battery_type"],i["ds_storage_system"],i["voltage"],i["nominal_capacity"],i["max_limit"],i["min_limit"],i["init_capacity"],i["max_hour_discharge"])
        lista.append(tupla)
    
    agente.ejecutarMuchos(sentenciaEnvio,lista)

    return

# Envio de la informacion de los usuarios
def envioUsr(agente,idComunidad, usuarios):
    sentenciaEnvio = " INSERT INTO leading_db.energy_community_consumer_profile (id_energy_community, id_consumer_profile) VALUES (%s, %s);"

    lista = []
    for i in usuarios:
        tupla = (idComunidad,i)
        lista.append(tupla)

    agente.ejecutarMuchos(sentenciaEnvio,lista)

    return

# Envio del proceso 
def envioPro(agente,idComunidad,proceso):
    sentenciaEnvio = " INSERT INTO leading_db.energy_community_process (id_energy_community, event_id, start) VALUES (%s, %s, %s);"
    tupla = (idComunidad,0,proceso)
    agente.ejecutarMuchos(sentenciaEnvio,[tupla])
    return proceso

# Envio de informacion a la base de datos
def envioDatos(comunidad,fotovoltaicos,eolicos,baterias,usuarios,proceso):
    agente = Agente_MySql()
    idComunidad = 0
    start = ""
    if any(comunidad):
        idComunidad = envioComu(agente,comunidad)
        st.write("ID de la comunidad: ", idComunidad)
    if any(fotovoltaicos) and idComunidad>0:
        envioGen(agente,fotovoltaicos,idComunidad,1)
    if any(eolicos) and idComunidad>0:
        envioGen(agente,eolicos,idComunidad,2)
    if any(baterias) and idComunidad>0:
        envioBat(agente,idComunidad,baterias)
    if any(usuarios) and idComunidad>0:
        envioUsr(agente,idComunidad,usuarios)
    if any(proceso) and idComunidad>0:
        start = envioPro(agente,idComunidad,proceso)
    
    logging.info("Hora: "+str(start)+" del tipo " + str(type(start)))
    logging.info("ID Comunidad: "+str(idComunidad))
    return idComunidad,start