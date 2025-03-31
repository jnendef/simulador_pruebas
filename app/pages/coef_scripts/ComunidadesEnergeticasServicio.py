#
#  Funciones para el funcionamiento del script de calculo de coeficientesd de reparto
#
#  @referencia fgregorio
#  @modificaciones jnaveiro
#
#

from pages.coef_scripts.DTOs.ComunidadEnergeticaDTO import ComunidadEnergeticaDTO
from pages.coef_scripts.DTOs.DatoConsumoUsuarioDTO import DatoConsumoUsuarioDTO
from pages.coef_scripts.DTOs.GeneradorEnergiaDTO import GeneradorEnergiaDTO
from pages.coef_scripts.DTOs.UsuarioDTO import UsuarioDTO

import datetime
import logging

# Funcion de obtencion de datos de la comunidad energetica desde la base de datos

def obtenerDatosComunidadEnergeticaDesdeBBDD (agenteEjecucionMySql, idComunidadEnergetica:str, fcSimulacionDesde:str, fcSimulacionHasta:str, Dias = 365, Horas = 24):
    """
        author: fdgregorio
        
        traductor: jnaveiro
    
        Definicion: Método encargado de obtener los distintos datos de la comunidad energética, incluyendo los diversos usuarios y generadores.
        
        Variables de entrada: agenteEjecucionMySql, idComunidadEnergetica(str), fcSimulacionDesde(str), fcSimulacionHasta(str)
        
        Variables de salida: comunidadEnergeticaReturned(ComunidadEnergeticaDTO)
        
        Objetos relevantes:
        
            1. comunidadEnergeticaReturned
            2. agenteEjecucionMySql
        
        Librerías que se utilizan:
        
            1. Simulador.DTOs.ComunidadEnergeticaDTO
            2. Simulador.DTOs.DatoConsumoUsuarioDTO
            3. Simulador.DTOs.GeneradorEnergiaDTO
            4. Simulador.DTOs.UsuarioDTO
            5. logging
    """
    try :

        # Declaramos el listado a devolver
        comunidadEnergeticaReturned = ComunidadEnergeticaDTO(dias=Dias,horas=Horas)

        # Paso 1: Obtenemos los datos relativos a la comunidad energética
        sqlDatosGeneralesCE = "SELECT CE.id_energy_community, CE.name, CE.min_participation, CE.max_participation, CE.energy_poverty " + " FROM leading_db.energy_community as CE" + " WHERE CE.id_energy_community = " + idComunidadEnergetica
        rs_comunidad = agenteEjecucionMySql.ejecutar(sqlDatosGeneralesCE)

        # Devolvemos los datos tratados
        for rs in rs_comunidad:

            # Declaramos el objeto a devolver en el listado
            comunidadEnergeticaReturned.setIdComunidadEnergetica(str(rs[0]))
            comunidadEnergeticaReturned.setDsComunidadEnergetica(str(rs[1]))
            comunidadEnergeticaReturned.setCuotaParticipacion_min(float(rs[2]))
            comunidadEnergeticaReturned.setCuotaParticipacion_max(float(rs[3]))
            comunidadEnergeticaReturned.setPorcentajeDedicadoPobrezaEnergetica(float(rs[4]))

            # Añadimos objeto relleno al listado
            # listComunidadEnergetica.add(comunidadEnergetica)

        # Paso 2: Obtenemos los datos relativos a los generadores de la comunidad
        sqlDatosGeneradorComunidad = "SELECT gen.id_generator, gen.description " + " FROM leading_db.generator as gen " + " WHERE gen.id_energy_community = " + idComunidadEnergetica
        rs_generadores = agenteEjecucionMySql.ejecutar(sqlDatosGeneradorComunidad)
        # Devolvemos los datos tratados
        for rs in rs_generadores:

            # Declaramos el objeto a devolver en el listado
            genEnergia = GeneradorEnergiaDTO(Dias = Dias,Horas = Horas)
            genEnergia.setIdGeneradorEnergia(str(rs[0]))
            genEnergia.setDsGeneradorEnergia(str(rs[1]))

            # Por cada generador los cargamos sus datos
            # private double consumos [][] = new double [3][7]
            sqlDatosGeneracionGenerador = "SELECT gen_data.timestamp, DAYOFYEAR (gen_data.timestamp) -1 as numDayYear, HOUR (gen_data.timestamp) as numHoraDia , gen_data.production " + "FROM leading_db.generator_data gen_data " + " WHERE gen_data.id_generator = " + genEnergia.getIdGeneradorEnergia() + " AND gen_data.timestamp>='" + fcSimulacionDesde + "' " + " AND gen_data.timestamp<='" + fcSimulacionHasta + "' "

            rs_generaciones_generador = agenteEjecucionMySql.ejecutar(sqlDatosGeneracionGenerador)
            # Devolvemos los datos tratados
            for rs2 in rs_generaciones_generador:

                iNumDiaConsumo = int(rs2[1])
                iNumHoraConsumo = int(rs2[2])
                production = float(rs2[3])

                genEnergia.getGeneracion()[iNumDiaConsumo-1][iNumHoraConsumo] = production

            # Añadimos objeto relleno al listado
            comunidadEnergeticaReturned.generadoresComunidad.append(genEnergia)
            
        # FIXME: Pendiente de validar, Paso 2.5: Estado del balance de las baterías
        battery = False
        sqlDatosBateriasComunidad = "SELECT batt.id_storage_system, batt.ds_storage_system " + " FROM leading_db.storage_system as batt " + " WHERE batt.id_energy_community = " + idComunidadEnergetica
        # Consulta si hay baterías de la hoja storage_system
        rs_baterias = agenteEjecucionMySql.ejecutar(sqlDatosBateriasComunidad)
        if len(rs_baterias)>0:
            battery = True

        if battery:
            # Recuperar, en caso de que haya baterías, los datos de la columna balance de la hoja   storage_system_cycle_data
            for rs in rs_baterias:
            # Declaramos el objeto a devolver en el listado
                batEnergia = GeneradorEnergiaDTO(Dias = Dias,Horas = Horas)
                batEnergia.setIdGeneradorEnergia(str(rs[0]))
                batEnergia.setDsGeneradorEnergia(str(rs[1]))
                
                #columna battery_energy_balance
                sqlDatosGeneracionBateria = "SELECT gen_data.timestamp, DAYOFYEAR (gen_data.timestamp) -1 as numDayYear, HOUR (gen_data.timestamp) as numHoraDia , gen_data.battery_energy_balance " + "FROM leading_db.storage_system_cycle_data as gen_data " + " WHERE gen_data.id_storage_system = " + batEnergia.getIdGeneradorEnergia() + " AND gen_data.timestamp>='" + fcSimulacionDesde + "' " + " AND   gen_data.timestamp<='" + fcSimulacionHasta + "' "

                rs_generaciones_bateria = agenteEjecucionMySql.ejecutar(sqlDatosGeneracionBateria)
                # Devolvemos los datos tratados
                for rs2 in rs_generaciones_bateria:

                    iNumDiaConsumo = int(rs2[1])
                    iNumHoraConsumo = int(rs2[2])
                    production = float(rs2[3])

                    # Sumarlo a los generadores
                    batEnergia.getGeneracion()[iNumDiaConsumo-1][iNumHoraConsumo] = production

                # Añadimos objeto relleno al listado
                comunidadEnergeticaReturned.generadoresComunidad.append(batEnergia)


        # Paso 3: Obtenemos los datos relativos a los usuarios de la comunidad
        sqlDatosUsuariosComunidad = "SELECT users.id_user, users.cups, CONCAT(users.name, ' ', users.surname1, ' ', users.surname2) as nombreCompleto "+ " FROM leading_db.user as users " + " where users.id_energy_community = " + idComunidadEnergetica

        rs_usuarios = agenteEjecucionMySql.ejecutar(sqlDatosUsuariosComunidad)
        # Devolvemos los datos tratados
        for rs in rs_usuarios:

            # Declaramos el objeto a devolver en el listado
            usuarioDTO = UsuarioDTO(Dias = Dias,Horas = Horas)
            usuarioDTO.setIdUsuario(str(rs[0]))
            usuarioDTO.setCupsUsuario(str(rs[1]))
            usuarioDTO.setDsUsuario(str(rs[2]))

            # Por cada usuario cargamos su lista de consumos
            # private double consumos [][] = new double [3][7]
            sqlConsumosUsuariosComunidad = "SELECT user_data.id_user_data, user_data.timestamp, DAYOFYEAR (user_data.timestamp) -1 as numDayYear, HOUR (user_data.timestamp) as numHoraDia , user_data.consumption, user_data.partition_coefficient, user_data.partition_energy, user_data.partition_surplus_energy " + "FROM leading_db.user_data as user_data " + "WHERE user_data.id_user = " + usuarioDTO.getIdUsuario() + " AND user_data.timestamp>='" + fcSimulacionDesde + "' " + " AND user_data.timestamp<='" + fcSimulacionHasta + "' "

            rs_consumos_usuarios = agenteEjecucionMySql.ejecutar(sqlConsumosUsuariosComunidad)
            # Devolvemos los datos tratados
            for rs2 in rs_consumos_usuarios:

                idUserData = int(rs2[0])
                fechaConsumo = str(rs2[1])
                iNumDiaConsumo = int(rs2[2])
                iNumHoraConsumo = int(rs2[3])
                energiaConsumidaUsuarioDiaHora = float(rs2[4])

                # Resto de variables aqui no hay que cargarlas (son null)
                datoConsumoUsuarioDTO = DatoConsumoUsuarioDTO()
                datoConsumoUsuarioDTO.setIdUserData(idUserData)
                datoConsumoUsuarioDTO.setFcDatoConsumoHorario(fechaConsumo)
                datoConsumoUsuarioDTO.setValorDatoConsumoHorario(energiaConsumidaUsuarioDiaHora)

                usuarioDTO.consumos[iNumDiaConsumo-1][iNumHoraConsumo] = datoConsumoUsuarioDTO

            
            # Añadimos objeto relleno al listado
            comunidadEnergeticaReturned.getUsuariosComunidad().append(usuarioDTO)
        

        # Devolvemos la lista rellena
        return comunidadEnergeticaReturned

    except Exception as e :
        mensajeExcepServ = "Error en el servicio: ComunidadesEnergeticasServicio.obtenerDatosComunidadEnergeticaDesdeBBDD "
        logging.error(mensajeExcepServ)
        logging.exception("Unexpected {}, {}".format(e,type(e)))

        raise SystemExit(e)

def almacenarDatosCalculadosTxt(ce,anyo):
    """
        author: fdgregorio
        
        traductor: jnaveiro
    
        Definicion: Metodo encargado de alamcenar en base de datos todos los cálculos realizados durante la simulacion junto al dato del consumo del usuario de la comunidad.
        
        Variables de entrada: agenteEjecucionMySql, ce(ComunidadEnergeticaDTO)
        
        Variables de salida: Ninguno
        
        Objetos relevantes:
        
            1. ce
            2. agenteEjecucionMySql
        
        Librerías que se utilizan:
        
            1. Simulador.DTOs.ComunidadEnergeticaDTO
            2. datetime
            3. logging
    """
    try:
        # Recorremos los distintos clientes de la comunidad
        with open("CAU"+str(ce.getIdComunidadEnergetica())+"_"+str(anyo)+".txt","w") as f:
            fecha0 = datetime.datetime(year=anyo,month=1,day=1,hour=0,minute=0,second=1)
            usuarios = ce.getUsuariosComunidad()
            for itUsuario in range(len(usuarios)):
                HorasSimul = 0
                fecha = datetime.datetime(year=anyo,month=1,day=1,hour=0,minute=0,second=1)
                consumosUsuarioIt = usuarios[itUsuario].getConsumos()
                numDias = len(consumosUsuarioIt)
                CUPS = usuarios[itUsuario].getCupsUsuario()

                for itDiaConsumo in range(numDias):
                    numHoras = len(consumosUsuarioIt[itDiaConsumo])
                    # if (fecha.month!=2 or fecha.day!=29):
                    for itHoraConsumo in range(numHoras):
                        coeficienteReparto = usuarios[itUsuario].getCoeficientesReparto()[itDiaConsumo][itHoraConsumo]
                        HorasSimul += 1
                        f.write("\n{:22s};{:4s};{:.6f}".format(CUPS[-22:],str(10000+HorasSimul)[-4:],coeficienteReparto/100))
                    
                    fecha += datetime.timedelta(days=1)

        # Elimina la primera linea en blanco
        g = open("CAU"+str(ce.getIdComunidadEnergetica())+"_"+str(anyo)+".txt","r")
        todo = g.readlines()
        g.close()
        with open("CAU"+str(ce.getIdComunidadEnergetica())+"_"+str(anyo)+".txt","w") as g:
            g.writelines(todo[1:])

        return "CAU"+str(ce.getIdComunidadEnergetica())+"_"+str(anyo)+".txt"

    except Exception as e:
        logging.error("ERROR EN EL ALMACENAJE EN TXT PASO 4: "+ str(e))

def almacenarDatosCalculadosComunidadEnergetica(agenteEjecucionMySql, ce):
    """
        author: fdgregorio
        
        modificaciones: jnaveiro
    
        Definicion: Metodo encargado de alamcenar en base de datos todos los cálculos realizados durante la simulacion junto al dato del consumo del usuario de la comunidad.
        
        Variables de entrada: agenteEjecucionMySql, ce(ComunidadEnergeticaDTO)
        
        Variables de salida: Ninguno
        
        Objetos relevantes:
        
            1. ce
            2. agenteEjecucionMySql
        
        Librerías que se utilizan:
        
            1. Simulador.DTOs.ComunidadEnergeticaDTO
            2. datetime
            3. logging
    """
    try:
        userN = len(ce.getUsuariosComunidad())
        # Recorremos los distintos clientes de la comunidad
        for itUsuario in range(userN):
            consumosUsuarioIt = ce.getUsuariosComunidad()[itUsuario].getConsumos()
            numDias = len(consumosUsuarioIt)
            id_user = ce.getUsuariosComunidad()[itUsuario].getIdUsuario()
            #Actualizar consumos
            sqlUpdateConsumos = " INSERT INTO leading_db.user_data (id_user, timestamp, consumption, partition_coefficient, partition_energy, partition_surplus_energy) VALUES (%s, %s, %s, %s, %s, %s);"
            listaInfo = []
            
            for itDiaConsumo in range(numDias):
                numHoras = len(consumosUsuarioIt[itDiaConsumo])
                for itHoraConsumo in range(numHoras):
                    coeficienteReparto = ce.getUsuariosComunidad()[itUsuario].getCoeficientesReparto()[itDiaConsumo][itHoraConsumo]
                    energiaRepartida = ce.getUsuariosComunidad()[itUsuario].getEnergiaReparto()[itDiaConsumo][itHoraConsumo]
                    energiaExcedente = ce.getUsuariosComunidad()[itUsuario].getEnergiaReparto_excedentes()[itDiaConsumo][itHoraConsumo]

                    # Solo si el día y la hora que en base de datos tienen consumos
                    if (consumosUsuarioIt[itDiaConsumo][itHoraConsumo] != None) :
                        # CODIGO OPTIMIZADO CON PK (da más o menos igual de rendimiento)                        
                        fechaAux = consumosUsuarioIt[itDiaConsumo][itHoraConsumo].getFcDatoConsumoHorario()
                        consumoAux = consumosUsuarioIt[itDiaConsumo][itHoraConsumo].getValorDatoConsumoHorario()
                        tuplaAux = (str(id_user),str(fechaAux),str(consumoAux),str(coeficienteReparto),str(energiaRepartida),str(energiaExcedente))
                        
                        listaInfo.append(tuplaAux)

            agenteEjecucionMySql.ejecutarMuchos(sqlUpdateConsumos,listaInfo)
        
        return True

    except Exception as e:
        logging.debug("ERROR EN LA INSERCION DE DATOS DE COEFICIENTES EN LA BASE DE DATOS EN EL PASO 4: "+str(e))
        return False

def compruebaSiEjecutar(agenteEjecucionMySql):
    """Funcion que comprueba si queda alguna comunidad por simular"""
    # Por cada usuario cargamos su lista de consumos
    # private double consumos [][] = new double [3][7]
    # Consultamos si nos toca ejecutar
    sqlCommunityProcess = "SELECT * FROM leading_db.energy_community_process a WHERE ((a.event_id = 35 AND a.result=1000) OR (a.event_id = 40 AND a.result =1001)) AND a.start = (SELECT max(b.start) FROM leading_db.energy_community_process b WHERE a.id_energy_community = b.id_energy_community)"

    rs_communityProcess = agenteEjecucionMySql.ejecutar(sqlCommunityProcess)

    vector_idEnergyCommunity = []

    for rs in rs_communityProcess:
        vector_idEnergyCommunity.append(int(rs[1]))

    return vector_idEnergyCommunity

def obtenerParametrosEjecucionSimulacion(agenteEjecucionMySql,id_EnergyCommunity,anyo):
    """
        author: fdgregorio
        
        traductor: jnaveiro
    
        Definicion: Método encargado de obtener lso parametros de ejecucion de base de datos y actualizar la fecha de comienzo de la ejecucion de la misma
        
        Variables de entrada: agenteEjecucionMySql,anyo(int)
        
        Variables de salida: stringToResult(list)
        
        Objetos relevantes: Ninguno
        
        Librerías que se utilizan:
        
            1. numpy
            2. datetime
            3. logging
    """
    
    stringToResult = []
    try:
        # Declaramos las variables a rellenar
        idEnergyCommunityProcess = ""
        idEnergyCommunity = str(id_EnergyCommunity)

        # DateFormat sdfMYSQL = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
        sFechaActual = datetime.datetime.now().__format__('%Y-%m-%d %H:%M:%S')

        sqlUpdateConsumos = "INSERT INTO leading_db.energy_community_process (id_energy_community, event_id, start) VALUES ( " + str(idEnergyCommunity) + ", 40, '" + sFechaActual + "') "

        agenteEjecucionMySql.ejecutar(sqlUpdateConsumos)
        agenteEjecucionMySql.commitTransaction()
        
        sqlConsulta = "SELECT id_energy_community_process FROM leading_db.energy_community_process WHERE (id_energy_community = "+str(idEnergyCommunity)+" AND event_id = 40 AND start = '" + sFechaActual + "');"
        auxiliar = agenteEjecucionMySql.ejecutar(sqlConsulta)
        idEnergyCommunityProcess = str(auxiliar[0][0])
        
        stringToResult.append(idEnergyCommunityProcess)
        stringToResult.append(idEnergyCommunity)
        stringToResult.append(str(anyo) + "-01-01" + " 00:00:00")
        stringToResult.append(str(anyo) + "-12-31" + " 23:59:59")
        stringToResult.append(sFechaActual)

        # Damos por finalizada la ejecucion
        return stringToResult
    
    except Exception as e:
        stringToResult = None
        logging.debug("ERROR EN LA ACTUALIZACION AL PROCESO 40 DEL PASO 4: "+str(e))
        return stringToResult

def eliminarDatosUsuarios(agenteEjecucionMySql,ComunidadEnergetica):
    # Eliminamos los registros previos de datos de los usuarios de la comunidad energetica
    try:
        for user in ComunidadEnergetica.usuariosComunidad:
            SentenciaSQL = "DELETE FROM leading_db.user_data WHERE id_user="+str(user.getIdUsuario())+";"
            agenteEjecucionMySql.ejecutar(SentenciaSQL)
            agenteEjecucionMySql.commitTransaction()

    except Exception as e:
        logging.debug("ERROR AL ELIMINAR DATOS DE USUARIOS EN EL PASO 4: "+str(e))