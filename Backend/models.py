from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

# 1. El plano para la tabla de JUGADORES
class JugadorDB(Base):
    __tablename__ = "jugadores" # Así se llamará la tabla en MySQL

    # Definimos las columnas
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, index=True) # unique=True evita nombres repetidos

# 2. El plano para la tabla de PARTIDAS
class PartidaDB(Base):
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, index=True)
    jugador1A = Column(String(50))
    jugador2A = Column(String(50))
    jugador1B = Column(String(50))
    jugador2B = Column(String(50))
    pareja_ganadora = Column(String(1))
    tipo_partida = Column(String(100))
    apuesta = Column(Float)
    fecha = Column(DateTime, default=datetime.datetime.now) # Genera la fecha automáticamente