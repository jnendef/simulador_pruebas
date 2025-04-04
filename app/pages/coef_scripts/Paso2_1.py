# 
# Paso para la creacion de los usuarios a partir de los perfiles o los datos horarios
# 
# @referencia fgregorio
# 
# @modificaciones jnaveiro
# 

import datetime as dt
from datetime import date, timedelta

import holidays
import os

import logging
from logging.handlers import RotatingFileHandler

# import pages.coef_scripts.agente_Basico as aB
import agente_Basico as aB

# Metodo para finalizar el proceso

def final1000(agente,fcStart,idComunidad):
    
    now = dt.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S') 
    sentenciaUpdate = "UPDATE leading_db.energy_community_process"
    sentenciaUpdate = sentenciaUpdate+ " SET stop = '" + now + "',"
    sentenciaUpdate = sentenciaUpdate+ " result = 1000 "
    sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 30 AND start='"+ fcStart + "'"
    agente.ejecutar(sentenciaUpdate)
    agente.commitTransaction()

    return

def final1001(agente,fcStart,idComunidad):
    # Actulizamos la entrada correspondiente al proceso
        
    now = dt.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S') 
    sentenciaUpdate = "UPDATE leading_db.energy_community_process"
    sentenciaUpdate = sentenciaUpdate+ " SET stop = '" + now + "',"
    sentenciaUpdate = sentenciaUpdate+ " result = 1001 "
    sentenciaUpdate = sentenciaUpdate+ " WHERE id_energy_community = " + str(idComunidad) + " AND event_id = 30 AND start='"+ fcStart + "';"
    agente.ejecutar(sentenciaUpdate)
    agente.commitTransaction()
    
    return

# Funcion que comprueba si hay comunidades pendientes de simulacion 

def compruebaSiEjecutar(agenteEjecucionMySql):
    # Por cada usuario cargamos su lista de consumos
    # Consultamos si nos toca ejecutar
    sqlCommunityProcess = "SELECT * FROM leading_db.energy_community_process a WHERE ((a.event_id = 10 AND a.result=1000) OR (a.event_id = 30 AND a.result =1001)) AND a.start = (SELECT max(b.start) FROM leading_db.energy_community_process b WHERE a.id_energy_community = b.id_energy_community)"

    rs_communityProcess = agenteEjecucionMySql.ejecutar(sqlCommunityProcess)

    vector_idEnergyCommunity = []

    for rs in rs_communityProcess:
        vector_idEnergyCommunity.append(int(rs[1]))

    return vector_idEnergyCommunity

# Creacion de usuario a partir de usuario tipo

def usuariosTipo(agente,idComunidad,id_consumer_profile):
    # Obtenemos de la secuencia de usuarios el id del usuario que se creará
    selectSecuenciaUser = "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'leading_db' AND TABLE_NAME = 'user';"
    agente.cursor.execute(selectSecuenciaUser)
    idNewUser = agente.cursor.fetchone()[0]

    # Creamos un nuevo usuario en base de datos
    sentenciaInsertNuevoUsuario = "INSERT INTO leading_db.user (id_energy_community, name, surname1, surname2,  nif, address, zip, tel, email, cups, energy_poverty_beneficiary, power_tariff_1, power_tariff_2, energy_tariff_p1, energy_tariff_p2, energy_tariff_p3,  exp_energy_tariff) VALUES ( "
    sentenciaInsertNuevoUsuario = sentenciaInsertNuevoUsuario + str(idComunidad) + ",   "
    sentenciaInsertNuevoUsuario = sentenciaInsertNuevoUsuario + " 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', '" +  str(id_consumer_profile) + "-" + str(idNewUser) + "' , 0, 0, 0, 0, 0, 0, 0);"

    agente.ejecutar(sentenciaInsertNuevoUsuario)
    agente.commitTransaction()

    InsertarDatos = True

    return idNewUser, InsertarDatos

# Creacion usuario con CUPS o modificacion para reutilizarlo

def usuariosXCUPS(agente,DescripcionPerfil,idComunidad):
    # Miramos si en la tabla user existe algún usuario con el cups que acabamos de  recuperar
    # Si existe, obtenemos el id_user
    InsertarDatos = True
    try:
        sentenciaObtenerIdUser = "SELECT id_user FROM leading_db.user where cups = '" + str(DescripcionPerfil) + "'"
        agente.cursor.execute(sentenciaObtenerIdUser)
        registroIdUser = agente.cursor.fetchone()
        idNewUser = registroIdUser[0]

        # UPDATE table_name
        SentenciaActualizar = "UPDATE leading_db.user "
        # SET column1 = value1, column2 = value2, ...
        SentenciaSet = "SET id_energy_community = " + str(idComunidad)
        # WHERE condition;
        SentenciaWhere = " WHERE id_user = " + str(int(idNewUser)) + ";"
        SentenciaActualizarFinal = SentenciaActualizar + SentenciaSet + SentenciaWhere

        agente.cursor.execute(SentenciaActualizarFinal)
        agente.commitTransaction
        InsertarDatos = False
        # Si no existe, generamos un nuevo registro en el que añadimos el cups del perfil

    except TypeError as e:
        # Obtenemos de la secuencia de usuarios el id del usuario que se creará
        selectSecuenciaUser = "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'leading_db' AND TABLE_NAME = 'user';"
        agente.cursor.execute(selectSecuenciaUser)
        idNewUser = agente.cursor.fetchone()[0]
        # Creamos un nuevo usuario en base de datos
        sentenciaInsertNuevoUsuario = "INSERT INTO leading_db.user (id_energy_community, name, surname1, surname2,  nif, address, zip, tel, email, cups, energy_poverty_beneficiary,  power_tariff_1, power_tariff_2, energy_tariff_p1, energy_tariff_p2,  energy_tariff_p3, exp_energy_tariff) VALUES ( "
        sentenciaInsertNuevoUsuario = sentenciaInsertNuevoUsuario + str(idComunidad)    + ", "
        sentenciaInsertNuevoUsuario = sentenciaInsertNuevoUsuario + " 'GEN_AUT',    'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT', 'GEN_AUT',   '" + str(DescripcionPerfil) + "', 0, 0, 0, 0, 0, 0, 0);"
        agente.cursor.execute(sentenciaInsertNuevoUsuario)
        agente.commitTransaction()

        InsertarDatos = True
    
    return idNewUser, InsertarDatos

### ---- METODO PARA HACER LA SELECT DE LA BASE DE DATOS QUE EXTRAE EL VALOR DE CONSUMO ----

def select_consumo (agente,id_consumer_profile, anyo, mes, dia, hora):
    
    sentenciaObtenerConsumo = "SELECT consumer_profile_consumption.consumption FROM leading_db.consumer_profile_consumption WHERE "
    sentenciaObtenerConsumo = sentenciaObtenerConsumo + "id_consumer_profile = " + str(id_consumer_profile)
    sentenciaObtenerConsumo = sentenciaObtenerConsumo + " AND year = " + str(anyo)
    sentenciaObtenerConsumo = sentenciaObtenerConsumo + " AND month = " + str(mes)
    sentenciaObtenerConsumo = sentenciaObtenerConsumo + " AND day = " + str(dia)
    sentenciaObtenerConsumo = sentenciaObtenerConsumo + " AND hour = " + str(hora) + ";"
    try:
        registroConsumo = agente.ejecutar(sentenciaObtenerConsumo)[0][0]
    except Exception as ex:
        logging.error("ERROR EN PASO 2, No se puede obtener el registro de consumo: ", exc_info=True)
    
    return registroConsumo

### ---- METODO PARA OBTENER EL VALOR DEL CONSUMO ADAPTADO ----

def consumoAdaptado (agente, id_consumer_profile, comunidadAutonoma:str, anyoDatos:int, anyoSimulacion:int, mes:int, dia:int, hora:int):
    """
    --------------------------------------------------------------------------
    Pasos a seguir
    --------------------------------------------------------------------------

    Parámetros de entrada: año, mes, dia, hora
    Salida: valor de consumo

    1.- De la fecha que se nos ha pasado como argumento y de la misma fecha del año anterior camos:
        *Año
        *Día de la semana    

    2.- Miramos si el día que se nos ha pasado por argumento es festivo

    3.- Si SI es festivo, miramos si ese día fue festivo el año anterior:
        3.1- Si fue festivo, asignamos los mismos consumos horarios que el año anterior
        3.2- Si no fue festivo:
            * Busco el domingo de antes de ese día del año anterior
            * Se asignan los consumos del domingo del año anterior

    4.- Si NO es festivo, miramos si ese día fue festivo el año anterior:
        4.1- Si NO fue festivo, le asignamos los consumos del mismo día de la semana más próximo
        al de ese mismo día del año anterior
        4.2- Si SI fue festivo:
            * Buscamos el mismo día de la semana que el año pasado fue anterior al festivo
            * Se asignan los consumos de ese día
    """

    # 1.- Vemos qué día de la semana es la fecha que se nos ha pasado en el año de la simulación y en el año del que se tienen los datos
    anyoAux = anyoDatos
    if anyoDatos == 0:
        anyoAux = 2023

    fechaAnyoSimulacion = date(anyoSimulacion,mes,dia)
    
    fechaAnyoDatos = date(anyoAux,mes,dia)

    # Localizamos los festivos del año de la simulación y del año de los datos en la comunidad autónoma de la instalación
    festivosAnyoSimulacion = holidays.ES(years=int(anyoSimulacion), prov=comunidadAutonoma)
    festivosAnyoDatos = holidays.ES(years=int(anyoAux), prov=comunidadAutonoma)

    # 2.- Miramos si el día que se nos ha pasado por argumento es festivo el año de la simulacion
    if fechaAnyoSimulacion in festivosAnyoSimulacion:
        # 3.- Si SI es festivo, miramos si ese día fue festivo el año anterior:
        if fechaAnyoDatos in festivosAnyoDatos: 
            # 3.1- Si fue festivo, asignamos los mismos consumos horarios que el año anterior
            anyoConsumo = anyoDatos
            mesConsumo = fechaAnyoDatos.month
            diaConsumo = fechaAnyoDatos.day
            horaConsumo = hora
            
            consumo_final = select_consumo (agente,id_consumer_profile, anyoConsumo, mesConsumo, diaConsumo, horaConsumo)          
            
        else: 
            # 3.2- Si no fue festivo:
            # Busco el domingo más próximo a ese día del año anterior           
            if fechaAnyoDatos.weekday() == 0:
                domingo_mas_cercano = fechaAnyoDatos - timedelta(days=1)
            elif fechaAnyoDatos.weekday() == 1:
                domingo_mas_cercano = fechaAnyoDatos - timedelta(days=2)
            elif fechaAnyoDatos.weekday() == 2:
                domingo_mas_cercano = fechaAnyoDatos - timedelta(days=3)
            else:
                dias_hasta_domingo = 6 - fechaAnyoDatos.weekday()
                domingo_mas_cercano = fechaAnyoDatos + timedelta(days=dias_hasta_domingo)
 
            # Se asignan los consumos del domingo del año anterior
            anyoConsumo = anyoDatos
            mesConsumo = domingo_mas_cercano.month
            diaConsumo = domingo_mas_cercano.day
            horaConsumo = hora
            
            consumo_final = select_consumo (agente,id_consumer_profile, anyoConsumo, mesConsumo, diaConsumo, horaConsumo)          

    # 4.- Si NO es festivo, miramos si ese día fue festivo el año anterior:
    else:
        # Calculamos la diferencia de dias entre una fecha del año de la simulacion y la misma fecha del año de los datos
        delta = fechaAnyoSimulacion.weekday() - fechaAnyoDatos.weekday()
        if delta < 0:
            nuevo_delta = 7 + delta
        else:
            nuevo_delta = delta
     
        # 4.2- Si SI fue festivo:
        if fechaAnyoDatos in festivosAnyoDatos: 
            # Buscamos el mismo día de la semana que el año pasado fue anterior al festivo
            fechaAnyoDatosaux = fechaAnyoDatos - timedelta(days=7-nuevo_delta)                  

            # Se asignan los consumos de ese día
            anyoConsumo = anyoDatos
            mesConsumo = fechaAnyoDatosaux.month
            diaConsumo = fechaAnyoDatosaux.day
            horaConsumo = hora
            
            consumo_final = select_consumo (agente,id_consumer_profile, anyoConsumo, mesConsumo, diaConsumo, horaConsumo)          
               
        # 4.1- Si NO fue festivo, le asignamos los consumos del mismo día de la semana más próximo al de ese mismo día del año anterior
        else: 
            fechaAnyoDatosaux = fechaAnyoDatos + timedelta(days=nuevo_delta)
            anyoConsumo = anyoDatos
            mesConsumo = fechaAnyoDatosaux.month
            diaConsumo = fechaAnyoDatosaux.day
            horaConsumo = hora
            
            consumo_final = select_consumo (agente,id_consumer_profile, anyoConsumo, mesConsumo, diaConsumo, horaConsumo)          
  
    return consumo_final


### ---- BLOQUE PRINCIPAL DEL PROGRAMA ----    

def Paso2(agente, idComunidad, bisiesto, anyo = 0):
    """
    Definicion: Esta funcion es la principal de ejecucion del proceso de generacion de los perfiles de usuarios. 
    
    Variables de entrada: agente, idComunidad, bisiesto
    
    Variables de salida: proceso,  VectorDatosConsumo
    
    Objetos relevantes:
    
        1. agenteEjecucionMySql
    
    Librerías que se llaman:

        1. agente_Basico
        2. datetime
        3. logging
        4. holidays
    """

    proceso = True
    VectorDatosConsumo = []

    try:

        # Impresión del mensaje de bienvenida
        logging.info (" --- COMIENZO PROCESO CREACION DE USUARIOS A PARTIR DE PERFILES CE " + str(idComunidad) + " --- ")

        # Establemos en el energy_community_process la fecha de comienzo

        fcStart = dt.datetime.now()
        fcStart = fcStart.strftime('%Y-%m-%d %H:%M:%S')
        sentenciaInsertNuevoRegistroProcess = "INSERT INTO leading_db.energy_community_process  (id_energy_community, event_id, start) VALUES ( "
        sentenciaInsertNuevoRegistroProcess = sentenciaInsertNuevoRegistroProcess + str (idComunidad) + ", 30, '" + fcStart + "') "
        agente.ejecutar(sentenciaInsertNuevoRegistroProcess)
        agente.commitTransaction()

        # Declaramos el año para el cual crearemos los datos de perfiles (se coge del timestamp)
        if anyo == 0:
            currentDateTime = dt.datetime.now()
            date_year = currentDateTime.date()
            anyoSimulacion = date_year.year
        else:
            anyoSimulacion = int(anyo)

        # Obtenemos la comunidad autónoma en la que se encuentra la comunidad energética que se quiere simular
        # --------------- FIXME: Hay que sacar las siglas de la comunidad autónoma de la base de    datos cuando se cree la nueva tabla ---------------------- 
        comunidadAutonoma = "AR"

        # Recuperamos los perfiles de consumo para esta comunidad   (energy_community_consumer_profile)
        sentenciaObtenerProfiles = "SELECT * FROM leading_db.energy_community_consumer_profile  WHERE id_energy_community = " + str(idComunidad)
        registroPerfile = agente.ejecutar(sentenciaObtenerProfiles)

        # Recorremos cada uno de los perfiles almacenados
        for entradaPerfil in registroPerfile:
            id_consumer_profile = entradaPerfil[2]

            # Obtenemos la descripción del id_consumer_profile
            sentenciaObtenerDescripcionPerfil = "SELECT description FROM leading_db.consumer_profile WHERE id_consumer_profile = " + str(id_consumer_profile)
            agente.cursor.execute(sentenciaObtenerDescripcionPerfil)
            registroDescripcionPerfil = agente.cursor.fetchone()
            DescripcionPerfil = registroDescripcionPerfil[0]
            
            idNewUser, InsertarDatos = usuariosTipo(agente,idComunidad,id_consumer_profile)

            # Obtenemos los datos del perfil y los asociamos al nuevo usuario
            sentenciaObtenerPerfilUsuario = "SELECT consumer_profile_consumption.year, consumer_profile_consumption.month, consumer_profile_consumption.day, consumer_profile_consumption.hour, consumer_profile_consumption.consumption FROM leading_db.consumer_profile_consumption WHERE id_consumer_profile = " + str(id_consumer_profile)

            registroDatosPerfilUsuario = agente.ejecutar(sentenciaObtenerPerfilUsuario)


            # Recorremos cada uno de los datos correspondientes al perfil y los almacenamos en un   vector de tuplas de datos

            for datoPerfilUsario in registroDatosPerfilUsuario:
                anyoDato = datoPerfilUsario[0]
                anyoDato = int(anyoDato)
                mes = datoPerfilUsario[1]
                mes = int(mes)
                dia = datoPerfilUsario[2]
                dia = int(dia)
                hora = datoPerfilUsario[3]
                hora = int(hora)
                salto = False

                if mes == 2 and dia ==29:       
                    # significa que tenemos datos reales de un año bisiesto
                    salto = True

                if not salto:
                    # Llamamos a la función que nos devuelve un consumo para la fecha   indicada a partir de los datos del año anterior y teniendo en  cuenta festivos y fines de semana
                    valorConsumo = consumoAdaptado (agente, id_consumer_profile, comunidadAutonoma, anyoDato, anyoSimulacion, mes,  dia, hora)

                    # Componemos la fecha a insertar
                    dateConsumo = date(anyoSimulacion, mes, dia)
                    dateConsumo = str(dateConsumo) + " " + str(hora) + ":" + "00:00"

                    #Componemos el vector de datos a insertar
                    TuplaVectorDatosConsumo = [str(idNewUser),str(dateConsumo),valorConsumo,0,0,0]
                    VectorDatosConsumo.append(TuplaVectorDatosConsumo)

                # Si el año es bisiesto, duplicamos los datos del día 28/02 en el día 29/02

                if bisiesto and mes==2 and dia==28:
                    # Componemos la fecha a insertar
                    dateConsumo = date(anyoSimulacion, 2, 29)
                    dateConsumo = str(dateConsumo) + " " + str(hora) + ":" + "00:00"

                    #Componemos el vector de datos a insertar
                    TuplaVectorDatosConsumo = [str(idNewUser),str(dateConsumo),valorConsumo,0,0,0]
                    VectorDatosConsumo.append(TuplaVectorDatosConsumo)

            # Ejecutamos el insert en base de datos para todos los datos del nuevo usuario    que están almacenados en el vector de datos a insertar
            sentenciaInsertNuevoDatoPerfil = "INSERT INTO leading_db.user_data (id_user, timestamp, consumption, partition_coefficient, partition_energy, partition_surplus_energy) VALUES(%s, %s, %s, %s, %s, %s)"
                    
            agente.ejecutarMuchos(sentenciaInsertNuevoDatoPerfil, VectorDatosConsumo)

        # Indicamos que la ejecución ha acabado correctamente
        final1000(agente,fcStart,idComunidad)

    ### PASO 8: Si ocurre un error lo indicamos
    except Exception as ex:
        proceso = False
        logging.error("ERROR EN PASO 2: EXCEPCION EN LA EJECUCION DEL PROCESO: ", exc_info=True)

        # Actulizamos la entrada correspondiente al proceso
        final1001(agente, fcStart, idComunidad)
    
    else:
        return proceso, VectorDatosConsumo
    
# if __name__ == "__main__":
#     path = os.getcwd()
#     direc = os.path.join(path,"logs")
#     if not os.path.exists(direc):
#         try:
#             os.mkdir(direc)
#         except Exception as e:
#             direc = path
    
#     logging.basicConfig(
#         level=logging.DEBUG,
#         handlers=[RotatingFileHandler(os.path.join(direc,'LEADING_PASO2_Output.log'), maxBytes=1000000, backupCount=4)],
#         format='%(asctime)s %(levelname)s %(message)s',
#         datefmt='%m/%d/%Y %I:%M:%S %p')

#     #Paso 0: Parametros generales de la simulación
#     #Obtenemos el agente de base de datos que utilizaremos durante toda la ejecución
#     agenteEjecucionMySql = aB.Agente_MySql()
#     # Obtenemos el anyo actual

#     currentDateTime = dt.datetime.now()
#     date_year = currentDateTime.date()
#     anyoSimulacionGuardarComunidad = date_year.strftime("%Y")
    
#     # Condicion de anyo bisiesto: el resto tiene que ser 0
    
#     resto = date_year.year % 4
#     bisiesto = False
#     if resto == 0:
#         bisiesto = True

#     ids_Comunidades = compruebaSiEjecutar(agenteEjecucionMySql)
#     Paso2(agenteEjecucionMySql,202, bisiesto, date_year.year)
#     # for ids in ids_Comunidades:
#     #     try:
#     #         Paso2(agenteEjecucionMySql,199, bisiesto, date_year.year)
#     #     except Exception as e:
#     #         logging.debug("Fallo Paso 2: " , exc_info=True)

#     agenteEjecucionMySql.cursor.close()