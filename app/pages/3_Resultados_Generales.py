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
