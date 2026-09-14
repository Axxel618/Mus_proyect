from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Backend.database import engine, SessionLocal, Base
from Backend import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

class JugadorCreate(BaseModel):
    nombre: str

class PartidaCreate(BaseModel):
    jugador1A: str
    jugador2A: str
    jugador1B: str
    jugador2B: str
    pareja_ganadora: str
    tipo_partida: str
    apuesta: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"mensaje": "¡El backend de Mus Tracker está funcionando a la perfección! 🃏"}

@app.get("/jugadores/")
def obtener_jugadores(db: Session = Depends(get_db)):
    jugadores_db = db.query(models.JugadorDB).all()
    nombres = [j.nombre for j in jugadores_db]
    return {"jugadores": nombres}

@app.post("/jugadores/")
def crear_jugador(jugador: JugadorCreate, db: Session = Depends(get_db)):
    jugador_existente = db.query(models.JugadorDB).filter(models.JugadorDB.nombre == jugador.nombre).first()
    if jugador_existente:
         raise HTTPException(status_code=400, detail="El jugador ya existe")
    
    nuevo_jugador = models.JugadorDB(nombre=jugador.nombre)
    db.add(nuevo_jugador)
    db.commit()
    return {"mensaje": "Jugador creado con éxito"}

@app.post("/partidas/")
def guardar_partida(partida: PartidaCreate, db: Session = Depends(get_db)):
    nueva_partida = models.PartidaDB(
        jugador1A=partida.jugador1A,
        jugador2A=partida.jugador2A,
        jugador1B=partida.jugador1B,
        jugador2B=partida.jugador2B,
        pareja_ganadora=partida.pareja_ganadora,
        tipo_partida=partida.tipo_partida,
        apuesta=partida.apuesta
    )
    
    db.add(nueva_partida)
    db.commit()
    return {"mensaje": "Partida guardada correctamente en la nube"}