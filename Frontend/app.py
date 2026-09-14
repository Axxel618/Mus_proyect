import streamlit as st
import requests
import pandas as pd

# URL oficial de tu backend en Render
API_URL = "https://mus-proyect.onrender.com"

st.title("🃏 Tracker de Partidas de Mus")

try:
    respuesta_jugadores = requests.get(f"{API_URL}/jugadores/")
    if respuesta_jugadores.status_code == 200:
        lista_jugadores = respuesta_jugadores.json().get("jugadores", [])
    else:
        lista_jugadores = []
except:
    lista_jugadores = []

tab1, tab2, tab3 = st.tabs(["🎮 Registrar Partida", "👤 Nuevo Jugador", "📈 Estadísticas"])

with tab1:
    st.write("Rellena los datos de la partida finalizada.")
    
    if not lista_jugadores:
        st.warning("⚠️ No hay jugadores registrados todavía o el backend está despertando. Añade un jugador en la pestaña de al lado.")
    
    with st.form("formulario_mus"):
        st.subheader("👥 Jugadores")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Pareja A")
            jugador1A = st.selectbox("Jugador 1 (A)", options=lista_jugadores if lista_jugadores else ["Esperando..."])
            jugador2A = st.selectbox("Jugador 2 (A)", options=lista_jugadores if lista_jugadores else ["Esperando..."])
            
        with col2:
            st.markdown("### Pareja B")
            jugador1B = st.selectbox("Jugador 1 (B)", options=lista_jugadores if lista_jugadores else ["Esperando..."])
            jugador2B = st.selectbox("Jugador 2 (B)", options=lista_jugadores if lista_jugadores else ["Esperando..."])
            
        st.subheader("📊 Detalles del Resultado")
        ganadores = st.selectbox("Pareja Ganadora", options=["A", "B"])
        tipo_partida = st.selectbox("Tipo de partida", options=["Normal", "Competitiva"])
        apuesta = st.number_input("Apuesta (€)", min_value=0.0, step=0.5)
        
        enviado = st.form_submit_button("💾 Guardar Partida")

    if enviado:
        if not lista_jugadores:
            st.error("❌ No se puede guardar la partida porque no hay jugadores cargados.")
        else:
            datos_partida = {
                "jugador1A": jugador1A,
                "jugador2A": jugador2A,
                "jugador1B": jugador1B,
                "jugador2B": jugador2B,
                "pareja_ganadora": ganadores,
                "tipo_partida": tipo_partida,
                "apuesta": apuesta
            }
            try:
                respuesta = requests.post(f"{API_URL}/partidas/", json=datos_partida)
                if respuesta.status_code == 200:
                    st.success("✅ ¡Partida guardada con éxito!")
                else:
                    st.error(f"❌ Error al guardar. El servidor dice: {respuesta.text}")
            except Exception as e:
                st.error("⚠️ No se ha podido conectar con el backend.")

with tab2:
    st.write("Añade un nuevo amigo a la base de datos.")
    
    with st.form("formulario_nuevo_jugador"):
        nuevo_nombre = st.text_input("Nombre del jugador")
        btn_nuevo_jugador = st.form_submit_button("➕ Añadir Jugador")
        
    if btn_nuevo_jugador:
        if nuevo_nombre.strip() == "":
            st.warning("⚠️ El nombre no puede estar vacío.")
        else:
            datos_jugador = {"nombre": nuevo_nombre.strip()}
            try:
                respuesta_jugador = requests.post(f"{API_URL}/jugadores/", json=datos_jugador)
                if respuesta_jugador.status_code == 200:
                    st.success(f"✅ ¡{nuevo_nombre.strip()} añadido a la base de datos! Recarga la página para verlos.")
                else:
                    st.error(f"❌ Error al añadir el jugador: {respuesta_jugador.text}")
            except Exception as e:
                st.error("⚠️ No se ha podido conectar con el backend.")

with tab3:
    st.header("🏆 Panel de Estadísticas")
    try:
        respuesta_partidas = requests.get(f"{API_URL}/partidas/")
        if respuesta_partidas.status_code == 200:
            partidas_json = respuesta_partidas.json()
            df = pd.DataFrame(partidas_json)
        else:
            df = pd.DataFrame()
        
        if df.empty:
            st.info("Aún no hay partidas registradas para calcular estadísticas.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error al leer las estadísticas: {e}")