### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt
import numpy as np

import base64

import logging

from datetime import datetime, timedelta

from pages.pages_content.page3 import desenlace

from pages.pages_content.page4 import obtencion_datos_usr, datos_matriz, preparacion_lista, obtencion_indices, grafico_prod_total,matrices_meses
from pages.pages_content.page4 import dataframes_datos, graficado_energia, graficado_coef, coeficientes_intervalo,grafico_genera_tot

meses = ["01-Ene", "02-Feb", "03-Mar", "04-Abr", "05-May", "06-Jun", "07-Jul", "08-Ago", "09-Sep", "10-Oct", "11-Nov", "12-Dic"]

tipologiaSB = {
    6:"Apartamento un adulto calefacción eléctrica",
    7:"Apartamento un adulto calefacción gas",
    9:"Piso dos adultos, uno o dos niños, calefacción electrica y aire AC",
    8:"Piso dos adultos, uno o dos niños, calefacción gas y aire AC",
    12:"Piso dos adultos, calefacción gas y AC",
    10:"Vivienda unifamiliar dos adultos, uno o dos niños, calefacción gas y AC"
}

st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

st.markdown("# Resultados")

with st.expander("Descarga de la información"):
    st.write("Este documento permite su descarga en formato PDF haciendo click en los tres puntos de la esquina superior derecha de la página web. Se desplegará un menú donde está la opción de imprimir, que es donde se tendrá la opción de descargarlo en formato PDF.")
    st.write("También es posible la descarga de los gráficos y las tablas pasando el ratón por la esquina superior derecha del gráfico o de la tabla. En el caso de las tablas aparecerán las opciones de maximizar y tres puntitos que al clickar mostrarán las opciones, entre las que se encuentran el guardar la imagen en formato png. En las tablas al pasar el ratón aparecerán en la esquina superior derecha tres opciones. La primera de esas opciones permite descargar la información de la tabla en formato csv.")

st.write(dt.datetime.today().__format__('%d %b %Y, %I:%M%p'))

try:
    st.markdown("## Comunidad: "+str(st.session_state.nComunidad))
    st.markdown("## Simulación para el Año: "+str(st.session_state.anyo))

    datosUsr = obtencion_datos_usr()

    redListaU, diccioUsr, mDatos = datos_matriz(datosUsr)

    eleccion = preparacion_lista(redListaU)

    consu = mDatos[diccioUsr[eleccion],:,0].copy()
    mconsutot  = matrices_meses(consu)
    gener = mDatos[diccioUsr[eleccion],:,2].copy()
    mgentot  = matrices_meses(gener)

    grafico_genera_tot(mgentot, mconsutot, meses)
    
    fecha_min = datetime(st.session_state.anyo, 1, 1, 0, 0)
    fecha_max = datetime(st.session_state.anyo+1, 1, 1, 0, 0) 
    
    st.markdown("### Análisis para intervalo concreto de fechas")

    # col1, col2 = st.columns(2)
    # with col1:
    #     start_time = st.date_input("Fecha inicio",value = fecha_min, min_value = fecha_min, max_value = fecha_max)
    # with col2:
    #     deltat = fecha_max-datetime(start_time.year, start_time.month, start_time.day, 0, 0)
    #     incremento = st.number_input("Intervalo días", value = 1, min_value = 1, max_value = deltat.days, step=1, format="%d")

    end_time = fecha_min + timedelta(360)

    df0, df1, df2, df3, df4 = dataframes_datos(fecha_min, end_time, eleccion, diccioUsr, mDatos)
    
    # indices = obtencion_indices(fecha_min, end_time)
    indices = meses.copy()
    
    st.markdown("### Gráfica de Generación Correspondiente, Excedentes y Autoconsumida")
    st.markdown("La gráfica a continuación contiene la generación que le corresponde al usuario de la comunidad seleccionado y cómo se distribuye su uso en Excedentes y Autoconsumida. Siendo los excedentes la energía vertida a red (que no ha consumido la comunidad) y la Autoconsumida la que ha podido aprovechar la comunidad. El resultado de la suma de Excedentes y Autoconsumida es la Generación Correspondiente.")
    graficado_energia(df0, df2, df3, df4, indices)
    
    st.markdown("### Coeficientes de reparto")
    st.markdown("Los coeficientes de reparto son los factores por los que se multiplica la producción para obtener el reparto de la energía producida. La elección del valor de estos coeficientes es decisión de la comunidad energética y se debe aceptar por parte de los miembros de ésta.")
    st.markdown("En este análisis se muestran los coeficientes promedios mensuales, que no tienen por qué coincidir con el coeficiente promedio anual por horas, que es el calculado en la pestaña de resultados generales.")
    graficado_coef(df1,indices)

    # st.markdown("## Coeficientes del intervalo")
    # cups = st.text_input("CUPS", value="", max_chars=22)
    # if cups != "" and len(cups)==22:
    #     coeficientes_intervalo(start_time, end_time,indices,df1, cups)

    desenlace()

except Exception as e:
    logging.debug("Problema para mostrar info usuarios:", exc_info=True)
    st.markdown("# Realice la simulación para obtener los resultados para su comunidad")
