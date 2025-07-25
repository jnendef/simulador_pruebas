### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import base64

import numpy as np
import pandas as pd

from pages.coef_scripts.agente_Basico import Agente_MySql

meses = ["01-Ene", "02-Feb", "03-Mar", "04-Abr", "05-May", "06-Jun", "07-Jul", "08-Ago", "09-Sep", "10-Oct", "11-Nov", "12-Dic"]

diccioTipo = {  "Apartamento_1adulto_calef_electrica" : 6,
                "Apartamento_1adulto_calef_gas" : 7,
                "Piso_2adultos_1-2niños_calef_electrica_aire_ac" : 9,
                "Piso_2adultos_1-2niños_calef_gas_aire_ac" : 8,
                "Piso_2adultos_calef_gas_aire_ac" : 12,
                "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac" : 10
            }

listaDiccioTipo = list(diccioTipo)

tipologiaSB0 = [
            "Apartamento un adulto calefacción eléctrica",
            "Apartamento un adulto calefacción gas",
            "Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
            "Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
            "Piso dos adultos, calefacción gas y AC",
            "Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
        ]

tipologiaSB = {
    6: "(1924.326 kWh/año)Apartamento un adulto calefacción eléctrica",
    7: "(745.992 kWh/año)Apartamento un adulto calefacción gas",
    9: "(5931.25 kWh/año)Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
    8: "(3059.416 kWh/año)Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
    12:"(1916.711 kWh/año)Piso dos adultos, calefacción gas y AC",
    10:"(3889.858 kWh/año)Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
}


def introduccion():
    st.markdown("Las comunidades energéticas son entidades jurídicas basadas en la participación abierta y voluntaria, autónomas y efectivamente controladas por socios o miembros que están situados en las proximidades de los proyectos de energías renovables que sean propiedad de dichas entidades jurídicas y que estas hayan desarrollado, cuyos socios o miembros sean personas físicas, pymes o autoridades locales, incluidos los municipios y cuya finalidad primordial sea proporcionar beneficios medioambientales, económicos o sociales a sus socios o miembros o a las zonas locales donde operan, en lugar de ganancias financieras.")

def desarrollo():
    st.markdown("Los resultados de este informe son previsiones que se realizan en base a consumos tipo que no tienen por qué coincidir con el consumo real de los usuarios. Es una aproximación que sirve de orientación para poder tomar una decisión respecto a la comunidad.")

def desenlace(meses2):
    st.write("\n")
    st.write("\n")
    st.markdown("###### Responsabilidades")
    st.markdown("###### Esta información es facilitada por endef mediante el uso de software libre desarrollado para el apoyo a las comunidades energéticas. Esta app es una herramienta informática diseñada para realizar simulaciones con fines informativos y educativos. Si bien se han implementado metodologías rigurosas para mejorar la precisión de los resultados, Endef no garantiza la exactitud ni idoneidad de los datos generados.")

    st.markdown("###### El usuario reconoce y acepta que:")

    st.markdown("###### - Uso Bajo Responsabilidad Propia: El usuario es el único responsable de la aplicación de los resultados.")

    st.markdown("###### - Limitación de Responsabilidad: En ningún caso Endef será responsable de daños directos, indirectos, incidentales, especiales o consecuentes, incluyendo, pero sin limitarse a, pérdidas económicas, interrupciones del negocio, daños a equipos o cualquier otro perjuicio derivado del uso o incapacidad de uso del software.")
    st.markdown("###### Al utilizar esta app, el usuario acepta esta exención de responsabilidad en su totalidad.")
    
    col1,col2,col3 = st.columns(3)

    with col1:
        st.write("Zaragoza, "+str(dt.datetime.today().day)+" de "+meses2[dt.datetime.today().month-1]+" de "+str(dt.datetime.today().year))
    
    with col3:
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.markdown(
            """<a href="https://endef.com/">
            <img src="data:;base64,{}" width="200">
            </a>""".format(
                base64.b64encode(open("path1.png", "rb").read()).decode()
            ),
            unsafe_allow_html=True,
        )

def obtencion_info_usuarios():
    with Agente_MySql() as agente:
        sentenciaSQLusr = "SELECT * FROM leading_db.user WHERE id_energy_community = "+str(st.session_state.idComunidad)+";"
        usuarios = agente.ejecutar(sentenciaSQLusr)

        datosUsr = []

        for i in usuarios:
            sentenciaSQLdatos = "SELECT * FROM leading_db.user_data WHERE id_user = "+str(i[0])+";"
            datos = agente.ejecutar(sentenciaSQLdatos)
            datosUsr.append((i[10],datos))
        
    return datosUsr

def paso_matriz(datosUsr):
    # listaUsr = []
    diccioUsr = {}
    redListaU = []
    mDatos = np.zeros((len(datosUsr),len(datosUsr[0][1]),4))

    for i in range(len(datosUsr)):
        claveUsr = datosUsr[i][0]
        #listaUsr.append(claveUsr)
        if claveUsr not in redListaU:
            redListaU.append(claveUsr)
        diccioUsr[claveUsr] = i
        for j in range(len(datosUsr[i][1])):
            for k,l in enumerate(datosUsr[i][1][j]):
                if k>2:
                    mDatos[i,j,k-3] = l

    return redListaU, mDatos

def preparacion_desplegable(redListaU):
    # Obtenemos los distintos usuarios de la informacion
    redLista = sorted(redListaU)
    redLista2 = []
    posiRedLista = []

    # Se obtienen los valores no repetidos de tipologias
    for j,i in enumerate(redLista):
        if int(i.split("-")[0]) not in redLista2:
            redLista2.append(int(i.split("-")[0]))
            posiRedLista.append(j)
    
    indicesUsr = [str(i)+"-"+str(tipologiaSB[int(j.split("-")[0])]) for i,j in enumerate(redListaU)]

    return indicesUsr

def texto_propio():
    st.markdown("### Consumos Totales Anuales Por Usuario")
    texto = "La comunidad de "+str(st.session_state.nComunidad)
    if st.session_state.informe["cantidadFV"] > 0.0:
        texto = texto + " cuenta con una potencia fotovoltaica instalada de "+str(st.session_state.informe["cantidadFV"])+"kW"
    if st.session_state.informe["cantidadEO"] > 0.0:
        texto = texto + ", la potencia eólica instalada es "+str(st.session_state.informe["cantidadEO"])+"kW"
    if st.session_state.informe["cantidadBat"] > 0.0:
        texto = texto + " y "+str(st.session_state.informe["cantidadBat"])+"kWh de almacenamiento"
    texto += "."

    st.markdown(texto)
    
    st.markdown(" En el siguiente gráfico de barras se pueden apreciar los valores de los consumos, generación correspondiente y energía autoconsumida, en valores totales anuales, para cada usuario de la comunidad, en kWh, para el año especificado en la simulación("+str(st.session_state.anyo)+").")

def grafico_tabla_consumos(indicesUsr,mConsumos,mReparto,mExcedentes):
    dfCon = pd.DataFrame(mConsumos,index=indicesUsr,columns=["2_Consumos"])
    dfRep = pd.DataFrame(mReparto,index=indicesUsr,columns=["1_Generación Correspondiente"])
    dfExc = pd.DataFrame(mExcedentes,index=indicesUsr,columns=["3_Autoconsumida"])
    dfF = dfRep.join(dfCon)
    dfF = dfF.join(dfExc)
    dfF2 = dfF.copy()
    dfF2.index = [i for i in range(len(mConsumos))]

    st.markdown("")
    st.markdown("*Gráfico 1. Valores de energía consumida, generación correspondiente y energía autoconsumida*")
    st.bar_chart(dfF2, horizontal = False, height = 500, width = 500, stack=False,color= [  "#FF9943","#4343FF","#28D06C"], x_label="Usuarios", y_label="kWh")

    indice = st.column_config.TextColumn(label="Usuarios",width="medium",required=True)
    consumos = st.column_config.NumberColumn(label="Consumos",width="small", format="%d kWh",required=True)
    autoconsumida = st.column_config.NumberColumn(label="Autoconsumida",width="small", format="%d kWh",required=True)
    generacion = st.column_config.NumberColumn(label="Generación",width="small", format="%d kWh",required=True)

    st.markdown("De forma tabulada, los valores totales anuales serían los indicados a continuación:")
    st.data_editor( 
                    dfF,
                    height = 43 * len(mConsumos),
                    width= 800,
                    hide_index=False,
                    column_config={
                        "_index": indice,
                        "1_Generación Correspondiente":generacion,
                        "2_Consumos":consumos,
                        "3_Autoconsumida":autoconsumida,
                    },
                )
    st.markdown("*Tabla 1. Valores de consumo, generación correspondiente y autoconsumida*")

def texto_coef():
    st.markdown("### Coeficientes de reparto")
    st.markdown("Los coeficientes de reparto son los factores por los que se multiplica la producción para obtener el reparto de la energía producida. La elección del valor de estos coeficientes es decisión de la comunidad energética y se debe aceptar por parte de los miembros de ésta.")
    st.markdown("En esta simulación se proponen los posibles coeficientes de reparto basando los cálculos en los consumos de los usuarios de la comunidad y distribuyendo la energía producida proporcionalmente a estos consumos. Con este cálculo se busca que haya el mínimo de excedente vertido a red porque permite sacar el mayor rendimiento a la producción.")
    st.markdown("El coeficiente máximo seleccionado para la simulación es **"+str(st.session_state.datoscomunidad["max_participation"])+"%** que consiste en el valor máximo que puede tomar en la simulación el coeficiente de reparto para un único usuario. Se puede poner esta restricción para el caso de que un usuario tenga un consumo muy superior y evitar que acapare toda la producción.")
    st.markdown("El coeficiente mínimo seleccionado para la simulación es **"+str(st.session_state.datoscomunidad["min_participation"])+"%** que consiste en el valor mínimo que puede tomar en la simulación el coeficiente de reparto para un único usuario. Se puede poner esta restricción para evitar que un usuario tenga muy poca participación debido a tener poco consumo.")
    st.markdown("El porcentaje dedicado a pobreza energética es **"+str(st.session_state.datoscomunidad["energy_poverty"])+"%** que es el porcentaje de energía que se dedicará para los casos seleccionados.")

def grafico_genera_tot(mgentot, mconsutot, indicesgen):
    st.write("A continuación se muestra el gráfico de consumo total de los usuarios y generación fotovoltaica para las plantas generadoras incluidas en la comunidad.")

    dfGen = pd.DataFrame(mgentot,index=indicesgen,columns=["Generacion"])
    dfCon = pd.DataFrame(mconsutot,index=indicesgen,columns=["Consumo"])
    dfCoef = dfCon.join(dfGen)

    indice = st.column_config.TextColumn(label="Mes",width="small",required=True)
    consumo = st.column_config.NumberColumn(label="Consumo",width="medium", format="%d kWh",required=True)
    generacion = st.column_config.NumberColumn(label="Generación",width="medium", format="%d kWh",required=True)

    st.markdown("*Gráfico 0. Consumo y generación por meses de la planta de generación*")
    st.bar_chart(dfCoef, horizontal = False, stack=False, height = 500, width = 500,color = [ "#4343FF", "#FF9943"], x_label="Meses", y_label="kWh",)

    st.markdown("De forma tabulada, los valores de generación y el consumo mensual total de la comunidad serían los indicados a continuación:")

    st.data_editor(
                    dfCoef,
                    column_config={
                        "_index": indice,
                        "Consumo": consumo,
                        "Generacion": generacion,
                    },
                    hide_index=False,
                    height = 43 * len(indicesgen),
                )
    st.markdown("*Tabla 0. Valores de consumo y generación por meses*")

def grafico_tabla_coef(mCoef,indicesUsr):
    dfCoef = pd.DataFrame(mCoef,index=indicesUsr,columns=["%"])
        
    dfCoef2 = dfCoef.copy()
    dfCoef2.index = [i for i in range(len(indicesUsr))]
    st.markdown("*Gráfico 2. Valores promedios anuales de coeficientes de reparto por usuario*")
    st.bar_chart(dfCoef2, horizontal = False, height = 500, width = 500,color = "#4343FF", x_label="Usuario", y_label="%",)

    st.markdown("De forma tabulada, los valores promedios anuales serían los indicados a continuación:")

    indice = st.column_config.TextColumn(label="Usuarios",width="medium",required=True)
    porcentaje = st.column_config.NumberColumn(label="Coeficiente [%]",width="medium", format="%.4f",required=True)

    st.data_editor(
                    dfCoef,
                    column_config={
                        "_index":indice,
                        "%": porcentaje,
                    },
                    hide_index=False,
                    height = 43 * len(indicesUsr),
                )
    st.markdown("*Tabla 2. Valores promedios anuales de coeficientes de reparto por usuario*")

def contenido_graficos():

    # Obtencion de la informacion de los usuarios
    datosUsr = obtencion_info_usuarios()

    # Paso de la informacion  de los usuarios a una matriz de 3 dimensiones
    redListaU, mDatos = paso_matriz(datosUsr)
    
    # mDatos[nhoras,nusuarios,(consumos,coeficientes,reparto energetico,excedentes)]
    mConsumos = [round(mDatos[i,:,0].sum(0)) for i in range(len(datosUsr))]
    mCoef = [mDatos[i,:,1].mean(0) for i in range(len(datosUsr))]
    mReparto = [mDatos[i,:,2].sum(0) for i in range(len(datosUsr))]
    # mExcedentes = [mDatos[i,:,3].sum(0) for i in range(len(datosUsr))]
    mAutocons = [(mDatos[i,:,2].sum(0) - mDatos[i,:,3].sum(0)) for i in range(len(datosUsr))]

    mConsumo12T = np.sum(mDatos[:,:,0].copy(),axis = 0)
    mReparto12T = np.sum(mDatos[:,:,2].copy(),axis = 0)
    repartotot = np.zeros(12)
    consutotot = np.zeros(12)
    for i in range(1,13):
        fechacero = dt.datetime(st.session_state.anyo,1,1,0,0)
        horaini = 24 * (dt.datetime(st.session_state.anyo + (i)//13,((i)%13) + ((i)//13),1,0,0)-fechacero).days
        horafin = 24 * (dt.datetime(st.session_state.anyo + (i+1)//13,((i+1)%13) + ((i+1)//13),1,0,0)-fechacero).days
        repartotot[i-1] = np.sum(mReparto12T[horaini:horafin])
        consutotot[i-1] = np.sum(mConsumo12T[horaini:horafin])

    # se prepara la lista de usuarios para el desplegable
    indicesUsr = preparacion_desplegable(redListaU)
    st.sidebar.write("")

    # Intentamos esta parte porque no sabemos si existen aun todas las variables
    try:
        # Grafico de la generación anual Total
        grafico_genera_tot(repartotot, consutotot, meses)

        # Texto personalizado para la comunidad de la simulacion
        texto_propio()

        # Contenido con graficos con los consumos, reparto y excedentes
        grafico_tabla_consumos(indicesUsr,mConsumos,mReparto,mAutocons)
        
        # Texto coeficientes de reparto
        texto_coef()

        # Grafico de los coeficientes de reparto
        grafico_tabla_coef(mCoef,indicesUsr)
        
    except:
        st.markdown("# Realice la simulación para ver los resultados")
