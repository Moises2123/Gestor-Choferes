from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime

app = Flask(__name__)

CHOFERES_ARCHIVO = 'choferes.csv'
HISTORIAL_ARCHIVO = 'historial.csv'

# Cargar choferes desde archivo CSV
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

# Guardar lista de choferes
def guardar_choferes(choferes):
    with open(CHOFERES_ARCHIVO, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'nombre', 'estado']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(choferes)

# Cargar historial como lista de diccionarios
def cargar_historial():
    try:
        with open(HISTORIAL_ARCHIVO, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return []

# Guardar historial completo
def guardar_historial(historial):
    with open(HISTORIAL_ARCHIVO, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['nombre', 'hora', 'fecha', 'accion', 'dirigencia', 'destino']
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
    accion = request.form.get('accion')  # Cambié de ['accion'] a .get()

    if not accion:
        return "Error: El campo 'accion' no fue enviado o está vacío.", 400

    destino = request.form.get('destino', '')
    dirigencia = request.form.get('dirigencia', '')

    now = datetime.now()
    hora = now.strftime('%H:%M:%S')
    fecha = now.strftime('%Y-%m-%d')

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
        'destino': destino
    }

    historial = cargar_historial()
    historial.append(nuevo_registro)
    guardar_historial(historial)

    return redirect('/')


@app.route("/eliminar/<int:indice>", methods=['POST'])
def eliminar(indice):
    historial = cargar_historial()
    if 0 <= indice < len(historial):
        historial.pop(indice)
        guardar_historial(historial)
    return redirect('/')

@app.route("/editar/<int:indice>", methods=['GET', 'POST'])
def editar(indice):
    historial = cargar_historial()

    if request.method == 'POST':
        # Actualizar el registro con los nuevos datos del formulario
        historial[indice] = {
            'nombre': request.form['nombre'],
            'hora': request.form['hora'],
            'fecha': request.form['fecha'],
            'accion': request.form['accion'],
            'dirigencia': request.form['dirigencia'],
            'destino': request.form['destino']
        }
        guardar_historial(historial)
        return redirect('/')

    # Obtener el registro para mostrar en el formulario
    registro = historial[indice]
    return render_template("editar.html", registro=registro, indice=indice)

if __name__ == '__main__':
    app.run(debug=True)
