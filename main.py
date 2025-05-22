from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime, timezone
import pytz
import os
import uvicorn
from backup_utils import backup_to_csv, backup_database

# Crear la app de FastAPI
app = FastAPI(title="Sistema de Gestión de Choferes")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar carpetas de plantillas y estáticos
templates = Jinja2Templates(directory="templates")
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de la zona horaria
peru_tz = pytz.timezone('America/Lima')

# Inicializar la base de datos
def init_db():
    conn = sqlite3.connect('choferes.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_chofer TEXT NOT NULL,
        tipo TEXT NOT NULL,
        destino TEXT NOT NULL,
        diligencia TEXT NOT NULL,
        sustento TEXT NOT NULL,
        solicitud TEXT NOT NULL,
        responsable TEXT NOT NULL,
        fecha_hora TEXT NOT NULL,
        fecha_registro TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Modelos de datos
class Registro(BaseModel):
    id: Optional[int] = None
    nombre_chofer: str
    tipo: str  # Entrada/Salida
    destino: str
    diligencia: str
    sustento: str
    solicitud: str
    responsable: str
    fecha_hora: Optional[str] = None
    fecha_registro: Optional[str] = None

class RegistroResponse(BaseModel):
    id: int
    nombre_chofer: str
    tipo: str
    destino: str
    diligencia: str
    sustento: str
    solicitud: str
    responsable: str
    fecha_hora: str
    fecha_registro: str

# Lista de choferes
CHOFERES = [
    "Morris Larrañaga Policarpio",
    "Saucedo Abad Florencio",
    "Rojas Gutierrez Hermes",
    "Paciffico Valles Publio Salvador",
    "Noronha Gomez Joao Andre",
    "Jhean Marco Guerra Vasquez",
    "Reategui Vasquez Javier"
]


# Obtener hora actual en Perú
def get_current_peru_time():
    utc_now = datetime.now(timezone.utc)
    peru_now = utc_now.astimezone(peru_tz)
    return peru_now.strftime("%Y-%m-%d %H:%M:%S")

# Obtener conexión a la base de datos
def get_db():
    conn = sqlite3.connect('choferes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Rutas
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "choferes": CHOFERES})

@app.post("/registros/")
async def crear_registro(registro: Registro):
    conn = get_db()
    cursor = conn.cursor()
    peru_time = get_current_peru_time()
    
    cursor.execute("""
    INSERT INTO registros (nombre_chofer, tipo, destino, diligencia, sustento, solicitud, responsable, fecha_hora, fecha_registro)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        registro.nombre_chofer, 
        registro.tipo, 
        registro.destino, 
        registro.diligencia, 
        registro.sustento, 
        registro.solicitud, 
        registro.responsable, 
        registro.fecha_hora or peru_time,
        peru_time
    ))
    
    registro_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Realizar respaldo
    backup_to_csv()
    backup_database()
    
    return {"id": registro_id, "mensaje": "Registro creado exitosamente"}

@app.get("/registros/", response_model=List[RegistroResponse])
async def listar_registros():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registros ORDER BY id DESC")
    
    registros = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return registros

@app.get("/registros/{registro_id}", response_model=RegistroResponse)
async def obtener_registro(registro_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registros WHERE id = ?", (registro_id,))
    registro = cursor.fetchone()
    conn.close()
    
    if registro is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    return dict(registro)

@app.put("/registros/{registro_id}")
async def actualizar_registro(registro_id: int, registro: Registro):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM registros WHERE id = ?", (registro_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    cursor.execute("""
    UPDATE registros
    SET nombre_chofer = ?, tipo = ?, destino = ?, diligencia = ?, sustento = ?, solicitud = ?, responsable = ?
    WHERE id = ?
    """, (
        registro.nombre_chofer,
        registro.tipo,
        registro.destino,
        registro.diligencia,
        registro.sustento,
        registro.solicitud,
        registro.responsable,
        registro_id
    ))
    
    conn.commit()
    conn.close()
    
    # Realizar respaldo
    backup_to_csv()
    backup_database()
    
    return {"mensaje": "Registro actualizado exitosamente"}

@app.delete("/registros/{registro_id}")
async def eliminar_registro(registro_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM registros WHERE id = ?", (registro_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    
    cursor.execute("DELETE FROM registros WHERE id = ?", (registro_id,))
    conn.commit()
    conn.close()
    
    # Realizar respaldo
    backup_to_csv()
    backup_database()
    
    return {"mensaje": "Registro eliminado exitosamente"}

# Inicializar la base de datos al inicio
@app.on_event("startup")
async def startup_event():
    init_db()

# Ejecutar la aplicación
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
