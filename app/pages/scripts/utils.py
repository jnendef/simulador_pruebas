from geopy.geocoders import Nominatim 
import streamlit as st
import time

# Guardamos el geolocator como recurso único
@st.cache_resource
def get_geolocator():
    return Nominatim(user_agent="simulador_PV")

geolocator = get_geolocator()

# Guardamos la última petición en caché global
@st.cache_resource
def get_rate_limiter():
    return {"last_request": 0.0}

rate_limiter = get_rate_limiter()

# Cacheamos los resultados de las direcciones
@st.cache_data
def geocode(direccion):
    # Respetar 1 req/s
    ahora = time.time()
    diff = ahora - rate_limiter["last_request"]
    if diff < 1.0:
        time.sleep(1.0 - diff)

    rate_limiter["last_request"] = time.time()
    return geolocator.geocode(direccion)
