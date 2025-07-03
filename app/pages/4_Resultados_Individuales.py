### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import base64

import logging

from datetime import datetime, timedelta

from pages.pages_content.page4 import obtencion_datos_usr, datos_matriz, preparacion_lista, obtencion_indices, grafico_prod_total
from pages.pages_content.page4 import dataframes_datos, graficado_energia, graficado_coef, coeficientes_intervalo

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
    fecha_min = datetime(st.session_state.anyo, 1, 1, 0, 0)
    fecha_max = datetime(st.session_state.anyo+1, 1, 1, 0, 0) 
    
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.date_input("Fecha inicio",value = fecha_min, min_value = fecha_min, max_value = fecha_max)
    with col2:
        deltat = fecha_max-datetime(start_time.year, start_time.month, start_time.day, 0, 0)
        incremento = st.number_input("Intervalo días", value = 1, min_value = 1, max_value = deltat.days, step=1, format="%d")

    end_time = start_time + timedelta(incremento)

    df0, df1, df2, df3, df4 = dataframes_datos(start_time, end_time, eleccion, diccioUsr, mDatos)
    
    indices = obtencion_indices(start_time, end_time)
    
    st.markdown("### Gráfica de Consumo, Generación Correspondiente y Excedentes")
    graficado_energia(df0, df2, df3, df4, indices)
    
    st.markdown("### Coeficientes de reparto")
    graficado_coef(df1,indices)

    st.markdown("## Coeficientes del intervalo")
    cups = st.text_input("CUPS", value="", max_chars=22)
    if cups != "" and len(cups)==22:
        coeficientes_intervalo(start_time, end_time,indices,df1, cups)

    col1,col2,col3 = st.columns(3)

    with col3:
        st.markdown(
            """<a href="https://endef.com/">
            <img src="data:;base64,{}" width="200">
            </a>""".format(
                base64.b64encode(open("path1.png", "rb").read()).decode()
            ),
            unsafe_allow_html=True,
        )

except Exception as e:
    logging.debug("Problema para mostrar info usuarios:", exc_info=True)
    st.markdown("# Realice la simulación para obtener los resultados para su comunidad")
