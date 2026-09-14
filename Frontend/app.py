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
            datos_individuales = []
            datos_parejas = []
            
            for _, row in df.iterrows():
                ganador = row['pareja_ganadora']
                apuesta = row['apuesta']
                
                win_A = 1 if ganador == 'A' else 0
                win_B = 1 if ganador == 'B' else 0
                dinero_A = apuesta if ganador == 'A' else -apuesta
                dinero_B = apuesta if ganador == 'B' else -apuesta
                
                pareja_A = " & ".join(sorted([row['jugador1A'], row['jugador2A']]))
                pareja_B = " & ".join(sorted([row['jugador1B'], row['jugador2B']]))
                
                datos_parejas.extend([
                    {'Pareja': pareja_A, 'Victorias': win_A, 'Partidas': 1},
                    {'Pareja': pareja_B, 'Victorias': win_B, 'Partidas': 1}
                ])
                
                for j in [row['jugador1A'], row['jugador2A']]:
                    datos_individuales.append({'Jugador': j, 'Victorias': win_A, 'Dinero': dinero_A})
                for j in [row['jugador1B'], row['jugador2B']]:
                    datos_individuales.append({'Jugador': j, 'Victorias': win_B, 'Dinero': dinero_B})
            
            df_ind = pd.DataFrame(datos_individuales)
            df_par = pd.DataFrame(datos_parejas)
            
            # --- AGRUPAMOS ESTADÍSTICAS ---
            stats_ind = df_ind.groupby('Jugador').agg(
                Partidas=('Victorias', 'count'),
                Victorias=('Victorias', 'sum'),
                Balance_Total_=('Dinero', 'sum')
            ).reset_index()
            stats_ind['% Victorias'] = ((stats_ind['Victorias'] / stats_ind['Partidas']) * 100).round(1)
            stats_ind = stats_ind.sort_values(by='Victorias', ascending=False)
            
            stats_par = df_par.groupby('Pareja').sum().reset_index()
            stats_par['% Victorias'] = ((stats_par['Victorias'] / stats_par['Partidas']) * 100).round(1)
            stats_par = stats_par.sort_values(by='Victorias', ascending=False)
            
            # --- SECCIÓN VISUAL MEJORADA ---
            st.subheader("💰 Resumen del Torneo")
            
            # Calculamos a los líderes
            mejor_jugador = stats_ind.iloc[0]
            mas_ganancias = stats_ind.sort_values(by='Balance_Total_€', ascending=False).iloc[0]
            mas_perdidas = stats_ind.sort_values(by='Balance_Total_€', ascending=True).iloc[0]
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("🥇 Más victorias", mejor_jugador['Jugador'], f"{int(mejor_jugador['Victorias'])} ganadas")
            col_m2.metric("💸 Rey de las Apuestas", mas_ganancias['Jugador'], f"+{mas_ganancias['Balance_Total_€']} €")
            col_m3.metric("📉 En bancarrota", mas_perdidas['Jugador'], f"{mas_perdidas['Balance_Total_€']} €")
            
            st.divider()
            
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.markdown("**Ranking Individual**")
                st.dataframe(stats_ind.set_index('Jugador'), use_container_width=True)
            with col_stats2:
                st.markdown("**Mejores Parejas**")
                st.dataframe(stats_par.set_index('Pareja'), use_container_width=True)
                
            st.divider()
            
            # --- GRÁFICO DE VICTORIAS ---
            st.subheader("📈 Gráfico de Victorias por Jugador")
            # Extraemos solo el nombre y las victorias para el gráfico
            datos_grafico = stats_ind[['Jugador', 'Victorias']].set_index('Jugador')
            st.bar_chart(datos_grafico)
                
    except Exception as e:
        st.error(f"Error al leer las estadísticas: {e}")