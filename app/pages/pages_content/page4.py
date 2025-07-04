### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import numpy as np
import pandas as pd

from pages.coef_scripts.agente_Basico import Agente_MySql

diccioTipo = {  "Apartamento_1adulto_calef_electrica" : 6,
                "Apartamento_1adulto_calef_gas" : 7,
                "Piso_2adultos_1-2niños_calef_electrica_aire_ac" : 9,
                "Piso_2adultos_1-2niños_calef_gas_aire_ac" : 8,
                "Piso_2adultos_calef_gas_aire_ac" : 12,
                "Viv_unif_2adultos_1-2niños_calef_gas_aire_ac" : 10
            }

listaDiccioTipo = list(diccioTipo)

tipologiaSB0 = [
            "(1924.326 kWh/año) Apartamento un adulto calefacción eléctrica",
            "( 745.992 kWh/año) Apartamento un adulto calefacción gas",
            "( 5931.25 kWh/año) Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
            "(3059.416 kWh/año) Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
            "(1916.711 kWh/año) Piso dos adultos, calefacción gas y AC",
            "(3889.858 kWh/año) Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
        ]

tipologiaSB = {
    6: "(1924.326 kWh/año) Apartamento un adulto calefacción eléctrica",
    7: "( 745.992 kWh/año) Apartamento un adulto calefacción gas",
    9: "( 5931.25 kWh/año) Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
    8: "(3059.416 kWh/año) Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
    12:"(1916.711 kWh/año) Piso dos adultos, calefacción gas y AC",
    10:"(3889.858 kWh/año) Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
}

def grafico_genera_tot(mgentot, mconsutot, indicesgen):
    st.write("A continuación se muestra el gráfico de consumo total de los usuarios y generación fotovoltaica para las plantas generadoras incluidas en la comunidad.")

    dfGen = pd.DataFrame(mgentot,index=indicesgen,columns=["Generacion[kWh]"])
    dfCon = pd.DataFrame(mconsutot,index=indicesgen,columns=["Consumo[kWh]"])
    dfCoef = dfCon.join(dfGen)

    st.markdown("*Gráfico 0. Consumo y generación por meses de la planta de generación*")
    st.bar_chart(dfCoef, horizontal = False, stack=False, height = 500, width = 500,color = [ "#4343FF", "#FF9943"], x_label="Meses", y_label="kWh",)

    st.markdown("De forma tabulada, los valores de generación y el consumo mensual total de la comunidad serían los indicados a continuación:")

    st.data_editor(
                    dfCoef,
                    column_config={
                        "_index": st.column_config.Column(
                            "Mes",
                            width="large",
                            required=True,
                        ),
                        "kWh": st.column_config.Column(
                            "Consumo",
                            width="medium",
                            required=True,
                        ),
                        "kWh": st.column_config.Column(
                            "Generación",
                            width="medium",
                            required=True,
                        )
                    },
                    hide_index=False,
                    height = 43 * len(indicesgen),
                )
    st.markdown("*Tabla 0. Valores de consumo y generación por meses*")


def obtencion_datos_usr():
    with Agente_MySql() as agente:
        sentenciaSQLusr = "SELECT * FROM leading_db.user WHERE id_energy_community = "+str(st.session_state.idComunidad)+";"
        usuarios = agente.ejecutar(sentenciaSQLusr)

        datosUsr = []

        for i in usuarios:
            sentenciaSQLdatos = "SELECT * FROM leading_db.user_data WHERE id_user = "+str(i[0])+";"
            datos = agente.ejecutar(sentenciaSQLdatos)
            datosUsr.append((i[10],datos))

    return datosUsr

def datos_matriz(datosUsr):
    diccioUsr = {}
    redListaU = []

    mDatos = np.zeros((len(datosUsr),len(datosUsr[0][1]),4))
    for i in range(len(datosUsr)):
        claveUsr = datosUsr[i][0]
        if claveUsr not in redListaU:
            redListaU.append(claveUsr)
        diccioUsr[claveUsr] = i
        for j in range(len(datosUsr[i][1])):
            for k,l in enumerate(datosUsr[i][1][j]):
                if k>2:
                    mDatos[i,j,k-3] = l

    return redListaU, diccioUsr, mDatos

def preparacion_lista(redListaU):
    # Obtenemos los distintos usuarios de la informacion
    redLista = sorted(redListaU)
    redLista2 = []
    posiRedLista = []

    # Se obtienen los valores no repetidos de tipologias
    for j,i in enumerate(redLista):
        if int(i.split("-")[0]) not in redLista2:
            redLista2.append(int(i.split("-")[0]))
            posiRedLista.append(j)
    
    # indicesUsr = [str(i)+" "+str(int(j.split("-")[1]))+" "+str(tipologiaSB[int(j.split("-")[0])]) for i,j in enumerate(redListaU)]
    
    st.markdown("### Datos por usuario")
    eleccion0 = st.selectbox("Tipo de Usuario",[tipologiaSB[i] for i in redLista2])
    st.sidebar.write("")
    eleccion = redLista[posiRedLista[redLista2.index(diccioTipo[listaDiccioTipo[tipologiaSB0.index(eleccion0)]])]]
    
    return eleccion

def fecha(hora,dia):
    salida = dia+dt.timedelta(hours = float(hora))
    return salida

def obtencion_indices(start_time, end_time):
    fecha_ini = dt.datetime(start_time.year,start_time.month,start_time.day,0,0,0)
    horasInicio = 24*(start_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horas = np.arange(start = 0,stop = (horasFin - horasInicio), step=1, dtype=int)
    indices = [fecha(i,fecha_ini) for i in horas]

    return indices

def grafico_prod_total(mDatos,start_time,end_time,indices):
    horasInicio = 24*(start_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days

    matrizaux = mDatos[:,horasInicio:horasFin,2]
    reparto = np.sum(matrizaux,axis=0)
    
    df = pd.DataFrame(reparto,columns=["Generación Correspondiente"])
    df.index = indices
    
    st.bar_chart(df, x_label="Horas", y_label= "kWh",color="#4343FF")

def matrices_meses(mDatos,diccioUsr,eleccion):
    mConsumo12T = mDatos[diccioUsr[eleccion],:,0].copy()
    mReparto12T = mDatos[diccioUsr[eleccion],:,2].copy()
    repartotot = np.zeros(12)
    consutotot = np.zeros(12)
    for i in range(1,13):
        fechacero = dt.datetime(st.session_state.anyo,1,1,0,0)
        horaini = 24 * (dt.datetime(st.session_state.anyo + (i)//13,((i)%13) + ((i)//13),1,0,0)-fechacero).days
        horafin = 24 * (dt.datetime(st.session_state.anyo + (i+1)//13,((i+1)%13) + ((i+1)//13),1,0,0)-fechacero).days
        repartotot[i-1] = np.round(np.sum(mReparto12T[horaini:horafin]))
        consutotot[i-1] = np.round(np.sum(mConsumo12T[horaini:horafin]))
    return consutotot, repartotot

def dataframes_datos(start_time, end_time, eleccion, diccioUsr, mDatos):
    horasInicio = 24*(start_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days

    df0 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,0],columns=["Consumo"])
    df1 = pd.DataFrame(np.round(mDatos[diccioUsr[eleccion],horasInicio:horasFin,1],4),columns=["Coeficiente"])
    df2 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,2],columns=["Generación Correspondiente"])
    df3 = pd.DataFrame(mDatos[diccioUsr[eleccion],horasInicio:horasFin,3],columns=["Excedentes"])
    df4 = df2.join(-1*df3)
    df4 = df4.join((-1*df0))

    return df0, df1, df2, df3, df4

def graficado_energia(df0, df2, df3, df4, indices):
    df0.index = indices
    df2.index = indices
    df3.index = indices
    df4.index = indices

    st.bar_chart(df4, x_label="Horas", y_label= "kWh", color= ["#4343FF", "#28D06C", "#FF9943"])

    st.write("Consumo Total en el intervalo kWh: {}".format(str(df0.sum()["Consumo"])[:6]))
    st.write("Generación Correspondiente Total en el intervalo kWh: {}".format(str(df2.sum()["Generación Correspondiente"])[:6]))
    st.write("Excedente Total en el intervalo kWh: {}".format(str(df3.sum()["Excedentes"])[:6]))

def graficado_coef(df1,indices):
    df1.index = indices
    st.line_chart(df1, x_label = "Horas", y_label = "%", color="#4343FF")
    st.write("Coeficiente Promedio en el intervalo en Porcentaje: {}".format(str(df1.mean()["Coeficiente"])[:6]))

def coeficientes_intervalo(start_time, end_time,indices,df1,cups):
    coeficientes = []
    horasInicio = 24*(start_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days
    horasFin = 24*(end_time-dt.datetime(st.session_state.anyo, 1, 1, 0, 0).date()).days

    horas = np.arange(start = horasInicio,stop = horasFin)
    for i,j in enumerate(horas):
        coeficientes.append([cups,str(10001+j)[-4:],"{:.6f}".format(df1["Coeficiente"][indices[i]]/100.0)])

    dfaux = pd.DataFrame(coeficientes,columns=["CUPS","hora","Coeficiente"])
    st.dataframe(dfaux,hide_index=True)

