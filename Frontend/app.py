import streamlit as st
import requests
import pandas as pd

st.title("🃏 Tracker de Partidas de Mus")

try:
    respuesta_jugadores = requests.get("http://127.0.0.1:8000/jugadores/")
    lista_jugadores = respuesta_jugadores.json()["jugadores"] 
except:
    st.error("⚠️ No se ha podido conectar con el servidor backend.")
    lista_jugadores = []

tab1, tab2, tab3 = st.tabs(["🎮 Registrar Partida", "👤 Nuevo Jugador", "📈 Estadísticas"])


with tab1:
    st.write("Rellena los datos de la partida finalizada.")
    
    with st.form("formulario_mus"):
        st.subheader("👥 Jugadores")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Pareja A")
            jugador1A = st.selectbox("Jugador 1 (A)", options=lista_jugadores)
            jugador2A = st.selectbox("Jugador 2 (A)", options=lista_jugadores)
            
        with col2:
            st.markdown("### Pareja B")
            jugador1B = st.selectbox("Jugador 1 (B)", options=lista_jugadores)
            jugador2B = st.selectbox("Jugador 2 (B)", options=lista_jugadores)
            
        st.subheader("📊 Detalles del Resultado")
        ganadores = st.selectbox("Pareja Ganadora", options=["A", "B"])
        tipo_partida = st.selectbox("Tipo de partida", options = ["Normal", "Competitiva"])
        apuesta = st.number_input("Apuesta (€)", min_value=0.0, step=0.5)
        
        enviado = st.form_submit_button("💾 Guardar Partida")

    if enviado:
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
            respuesta = requests.post("http://127.0.0.1:8000/partidas/", json=datos_partida)
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
        
        # Botón para este formulario específico
        btn_nuevo_jugador = st.form_submit_button("➕ Añadir Jugador")
        
    if btn_nuevo_jugador:
        if nuevo_nombre.strip() == "":
            st.warning("⚠️ El nombre no puede estar vacío.")
        else:
            datos_jugador = {"nombre": nuevo_nombre.strip()}
            
            try:
                # Llamamos al endpoint de jugadores
                respuesta_jugador = requests.post("http://127.0.0.1:8000/jugadores/", json=datos_jugador)
                
                if respuesta_jugador.status_code == 200:
                    st.success(f"✅ ¡{nuevo_nombre} añadido a la base de datos!")
                else:
                    st.error("❌ Error al añadir el jugador.")
            except Exception as e:
                st.error("⚠️ No se ha podido conectar con el backend.")

with tab3:
    st.header("🏆 Panel de Estadísticas")
    
    try:
        # Leemos el archivo directamente con Pandas
        df = pd.read_csv("Data/datos_mus.csv")
        
        if df.empty:
            st.info("Aún no hay partidas registradas para calcular estadísticas.")
        else:
            # Listas para guardar los datos desplegados
            datos_individuales = []
            datos_parejas = []
            
            # Recorremos cada partida
            for _, row in df.iterrows():
                ganador = row['pareja_ganadora']
                apuesta = row['apuesta']
                fecha = row['fecha']
                
                # Definimos quién gana y cuánto dinero
                win_A = 1 if ganador == 'A' else 0
                win_B = 1 if ganador == 'B' else 0
                dinero_A = apuesta if ganador == 'A' else -apuesta
                dinero_B = apuesta if ganador == 'B' else -apuesta
                
                # Nombres de parejas ordenados alfabéticamente (para que A&B sea igual que B&A)
                pareja_A = " & ".join(sorted([row['jugador1A'], row['jugador2A']]))
                pareja_B = " & ".join(sorted([row['jugador1B'], row['jugador2B']]))
                
                # Guardamos datos de Parejas
                datos_parejas.extend([
                    {'Pareja': pareja_A, 'Victorias': win_A, 'Partidas': 1},
                    {'Pareja': pareja_B, 'Victorias': win_B, 'Partidas': 1}
                ])
                
                # Guardamos datos Individuales
                for j in [row['jugador1A'], row['jugador2A']]:
                    datos_individuales.append({'Fecha': fecha, 'Jugador': j, 'Victorias': win_A, 'Dinero': dinero_A})
                for j in [row['jugador1B'], row['jugador2B']]:
                    datos_individuales.append({'Fecha': fecha, 'Jugador': j, 'Victorias': win_B, 'Dinero': dinero_B})
            
            # Convertimos las listas a Tablas de Pandas (DataFrames)
            df_ind = pd.DataFrame(datos_individuales)
            df_par = pd.DataFrame(datos_parejas)
            
            # --- CÁLCULOS ---
            # 1. Ranking Individual
            stats_ind = df_ind.groupby('Jugador').agg(
                Partidas=('Victorias', 'count'),
                Victorias=('Victorias', 'sum'),
                Balance_Total=('Dinero', 'sum')
            ).reset_index()
            stats_ind['% Victorias'] = ((stats_ind['Victorias'] / stats_ind['Partidas']) * 100).round(1)
            stats_ind = stats_ind.sort_values(by='Victorias', ascending=False)
            
            # 2. Ranking de Parejas
            stats_par = df_par.groupby('Pareja').sum().reset_index()
            stats_par['% Victorias'] = ((stats_par['Victorias'] / stats_par['Partidas']) * 100).round(1)
            stats_par = stats_par.sort_values(by='Victorias', ascending=False)
            
            # --- INTERFAZ VISUAL ---
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.subheader("🥇 Ranking Individual")
                st.dataframe(stats_ind.set_index('Jugador'), use_container_width=True)
            with col_stats2:
                st.subheader("🤝 Mejores Parejas")
                st.dataframe(stats_par.set_index('Pareja'), use_container_width=True)
                
            st.divider()
            
            # 3. Gráfico de Trayectoria (Suma acumulada de victorias por fecha)
            st.subheader("📈 Trayectoria de Victorias")
            # Ordenamos por fecha y calculamos victorias acumuladas por jugador
            df_ind = df_ind.sort_values('Fecha')
            df_ind['Victorias Acumuladas'] = df_ind.groupby('Jugador')['Victorias'].cumsum()
            
            # Preparamos la tabla para el gráfico
            grafico_datos = df_ind.pivot_table(index='Fecha', columns='Jugador', values='Victorias Acumuladas', aggfunc='last').ffill().fillna(0)
            st.line_chart(grafico_datos)
            
    except Exception as e:
        st.error(f"Error al leer las estadísticas: {e}")