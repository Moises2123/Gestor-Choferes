from flask import Flask, render_template, request, redirect, flash, jsonify
import csv
from datetime import datetime, timezone
import pytz

app = Flask(__name__)
app.secret_key = 'clave_secreta'

CHOFERES_ARCHIVO = 'choferes.csv'
HISTORIAL_ARCHIVO = 'historial.csv'

def cargar_choferes():
    choferes = []
    try:
        with open(CHOFERES_ARCHIVO, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                choferes.append(row)
    except FileNotFoundError:
        pass
    return choferes

def guardar_choferes(choferes):
    with open(CHOFERES_ARCHIVO, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'nombre', 'estado']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(choferes)

def cargar_historial():
    try:
        with open(HISTORIAL_ARCHIVO, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return []

def guardar_historial(historial):
    with open(HISTORIAL_ARCHIVO, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'nombre', 'hora', 'fecha', 'accion', 'dirigencia', 'destino',
            'sustento', 'solicitud_movilidad', 'quien_dirige'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(historial)

@app.route("/")
def index():
    choferes = cargar_choferes()
    historial = cargar_historial()
    return render_template("index.html", choferes=choferes, historial=historial)

@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form.get('nombre')
    accion = request.form.get('accion')
    destino = request.form.get('destino', '').strip()
    dirigencia = request.form.get('dirigencia', '').strip()
    sustento = request.form.get('sustento', '').strip()
    solicitud_movilidad = request.form.get('solicitud_movilidad', '').strip()
    quien_dirige = request.form.get('quien_dirige', '').strip()
    hora_evento = request.form.get('hora_evento')
    fecha_evento = request.form.get('fecha_evento')

    if not nombre or not accion:
        flash('El nombre y la acción son obligatorios.')
        return redirect('/')

    if hora_evento and fecha_evento:
        hora = hora_evento
        fecha = fecha_evento
    else:
        now_utc = datetime.now(timezone.utc)
        peru_timezone = pytz.timezone('America/Lima')
        now_peru = now_utc.astimezone(peru_timezone)
        hora = now_peru.strftime('%H:%M:%S')
        fecha = now_peru.strftime('%Y-%m-%d')

    choferes = cargar_choferes()
    for chofer in choferes:
        if chofer['nombre'] == nombre:
            chofer['estado'] = 'ocupado' if accion == 'salida' else 'disponible'
            break
    guardar_choferes(choferes)

    nuevo_registro = {
        'nombre': nombre,
        'hora': hora,
        'fecha': fecha,
        'accion': accion,
        'dirigencia': dirigencia,
        'destino': destino,
        'sustento': sustento,
        'solicitud_movilidad': solicitud_movilidad,
        'quien_dirige': quien_dirige
    }

    historial = cargar_historial()
    historial.append(nuevo_registro)
    guardar_historial(historial)

    # Devuelve los datos del nuevo registro como JSON junto con el índice
    return jsonify({
        'registro': nuevo_registro,
        'indice': len(historial) - 1
    })

@app.route("/eliminar/<int:indice>", methods=['POST'])
def eliminar(indice):
    historial = cargar_historial()
    if 0 <= indice < len(historial):
        historial.pop(indice)
        guardar_historial(historial)
        flash('Registro eliminado exitosamente.')
    else:
        flash('Error: Índice de registro inválido.')
    return redirect('/')

@app.route("/editar/<int:indice>", methods=['GET', 'POST'])
def editar(indice):
    historial = cargar_historial()

    if not (0 <= indice < len(historial)):
        flash('Error: Índice de registro inválido.')
        return redirect('/')

    if request.method == 'POST':
        # Captura todos los campos, incluyendo quien_dirige
        historial[indice] = {
            'nombre': request.form.get('nombre', ''),
            'hora': request.form.get('hora', ''),
            'fecha': request.form.get('fecha', ''),
            'accion': request.form.get('accion', ''),
            'dirigencia': request.form.get('dirigencia', ''),
            'destino': request.form.get('destino', ''),
            'sustento': request.form.get('sustento', ''),
            'solicitud_movilidad': request.form.get('solicitud_movilidad', ''),
            'quien_dirige': request.form.get('quien_dirige', '')
        }
        guardar_historial(historial)
        flash('Registro editado exitosamente.')
        return redirect('/')

    registro = historial[indice]
    return render_template("editar.html", registro=registro, indice=indice)

if __name__ == '__main__':
    app.run(debug=True)
