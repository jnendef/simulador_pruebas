import streamlit as st

# import os
import logging

from pages.coef_scripts.agente_Basico import Agente_MySql

from pages.coef_scripts.Paso0_Comprobacion import comprobacionDb

from pages.coef_scripts.Paso1_EstimProd import Paso1
from pages.coef_scripts.Paso2_UserByProfile import Paso2
from pages.coef_scripts.Paso3_Baterias import Paso3
from pages.coef_scripts.Paso4_CalcCoef import Paso4

# Obtenciion de informacion de inicio del programa
def obtInfoInicio(agente,start):
    sentenciaObtenerIdComunidad = "SELECT * FROM leading_db.energy_community_process WHERE event_id = 0 AND start = '" + start + "';"

    records = agente.ejecutar(sentenciaObtenerIdComunidad)

    return records

# Calculo a partir de los datos
def calcula2(start, date_year):
    logging.info("Comienzo de los calculos")

    # Inicia la barra de estado
    status = st.progress(0)

    #Obtenemos el agente de base de datos que utilizaremos durante toda la ejecucion
    with Agente_MySql() as agenteEjecucionMySql:
        logging.debug(type(agenteEjecucionMySql))
        # Obtenemos el anyo
        try:
            agenteEjecucionMySql.isValidConection()
        except Exception as e:
            logging.error("No se ha conectado:", exc_info=True)
        
        anyoDatosGuardarComunidad = str(date_year)
        
        # Condicion de anyo bisiesto: el resto tiene que ser 0
        proceso1=False
        proceso2=False
        proceso3=False
        proceso4=False
        
        resto = date_year % 4
        bisiesto = False
        if resto == 0:
            bisiesto = True

        records = obtInfoInicio(agenteEjecucionMySql, start)
        logging.info("Info de inicio recopilada")
        if records != None:
            for i in records:
                logging.info("Comprobacion previa")
                okey,datos,datosUs,datosCe,datosGen,datosBat =comprobacionDb(agenteEjecucionMySql,i)
                if okey:
                    try:
                        proceso1, VectorDatosProduccion, idComunidad = Paso1(agenteEjecucionMySql,i,anyoDatosGuardarComunidad,bisiesto)
                        status.progress(25)
                    except Exception as e:
                        logging.error("Error en el proceso 1: ", exc_info=True)
                        st.error("Fallo en el Paso 1 del proceso, refresce la página, vuelva a cumplimentar y compruebe su conexión a internet.Si se repite el fallo, consulte con el proveedor.")
                else:
                    st.error("Faltan datos por completar o hay algún otro error. Comprobar logs.")
        else:
            logging.info("No se encontró nada para simular con fecha: "+start)

        if proceso1:
            try:
                proceso2, VectorDatosConsumo = Paso2(agenteEjecucionMySql, idComunidad, bisiesto,anyoDatosGuardarComunidad)
                status.progress(50)
            except Exception as e:
                logging.error("Error en el proceso 2: ", exc_info=True)
                st.error("Fallo en el Paso 2 del proceso, refresce la página, vuelva a cumplimentar y compruebe su conexión a internet.Si se repite el fallo, consulte con el proveedor.")
        else:
            st.error("Fallo en el Paso 1 del proceso, refresce la página, vuelva a cumplimentar y compruebe su conexión a internet.")
            return False
        if proceso2:
            try:
                proceso3, VectorDatosBaterias = Paso3(agenteEjecucionMySql,idComunidad)
                status.progress(75)
            except Exception as e:
                logging.error("Error en el proceso 3: ", exc_info=True)
                st.error("Fallo en el Paso 3 del proceso, refresce la página, vuelva a cumplimentar y compruebe su conexión a internet. Si se repite el fallo, consulte con el proveedor.")
        else:
            st.error("Fallo en el Paso 2 del proceso, refresce la página, vuelva a cumplimentar y compruebe su conexión a internet.")
            return False
        if proceso3:
            try:
                proceso4, ComunidadEnergetica = Paso4(agenteEjecucionMySql,anyoDatosGuardarComunidad,idComunidad,bisiesto)
                status.progress(100)
                st.success('¡Simulación completa!', icon="✅")
            except Exception as e:
                logging.error("Error en el proceso 4: ", exc_info=True)
                st.error("Fallo en el Paso 4 del proceso, refresce la página, vuelva a cumplimentar y compruebe su conexión a internet.Si se repite el fallo, consulte con el proveedor.")
        else:
            st.error("Fallo en el Paso 3 del proceso, refresce la página, vuelva a cumplimentar y compruebe su conexión a internet.")
            return False
        
        if not proceso4:
            st.error("Fallo en el Paso 4 del proceso, refresce la página, vuelva a cumplimentar y compruebe su conexión a internet.")
            return False
        
        return True