### Codigo desarrollado e implementado por Jose Manuel Naveiro Gomez
### josemanuel.naveiro@endef.com

import streamlit as st
import datetime as dt

import base64

from pages.pages_content.page3 import introduccion, desarrollo, contenido_graficos, desenlace



st.sidebar.markdown(
    """<a href="https://endef.com/">
    <img src="data:;base64,{}" width="200">
    </a>""".format(
        base64.b64encode(open("path1.png", "rb").read()).decode()
    ),
    unsafe_allow_html=True,
)

st.markdown("# Análisis de Comunidad")

with st.expander("Descarga de la información"):
    st.write("Este documento permite su descarga en formato PDF haciendo click en los tres puntos de la esquina superior derecha de la página web. Se desplegará un menú donde está la opción de imprimir, que es donde se tendrá la opción de descargarlo en formato PDF.")
    st.write("También es posible la descarga de los gráficos y las tablas pasando el ratón por la esquina superior derecha del gráfico o de la tabla. En el caso de las tablas aparecerán las opciones de maximizar y tres puntitos que al clickar mostrarán las opciones, entre las que se encuentran el guardar la imagen en formato png. En las tablas al pasar el ratón aparecerán en la esquina superior derecha tres opciones. La primera de esas opciones permite descargar la información de la tabla en formato csv.")

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

st.write("Zaragoza, "+str(dt.datetime.today().day)+" de "+meses[dt.datetime.today().month-1]+" de "+str(dt.datetime.today().year))
try:
    st.markdown("## Comunidad "+str(st.session_state.nComunidad))

    introduccion()

    st.markdown("## Simulación para el año "+str(st.session_state.anyo))

    desarrollo()

    if st.session_state.idComunidad>0:
        contenido_graficos()
    else:
        st.markdown("# Realice la simulación para obtener los resultados para su comunidad")

    desenlace()
except:
    st.markdown("# Realice la simulación para obtener los resultados para su comunidad")
