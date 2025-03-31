
import pandas as pd
import streamlit as st
from string import punctuation

# definicion de las funciones
def borrar(campo,valores):
    # st.session_state[campo].remove(valores)
    if len(st.session_state[campo])>0:
        st.session_state[campo].pop(-1)
    else:
        pass
    return 

def resetear(campo):
    st.session_state[campo] = []
    return

def actualizarValores(AddElem,listaElem,infoElem):
    if AddElem:
        infoElem.append(listaElem)

    return infoElem

def comprobarStrings(mensaje):
    return any(caracter in punctuation for caracter in mensaje)

def camposDataframe(concepto, datos, columnas, add = True):
    st.session_state[concepto] = actualizarValores(add,datos,st.session_state[concepto])
    
    info = st.session_state[concepto]
    df = pd.DataFrame(info, columns=columnas)
    
    return df