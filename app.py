from flask import Flask, render_template, request, redirect, flash
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Necesaria para usar flash

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
        pass  # Si el archivo no existe, simplemente retorna una lista vacía
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
    accion = request.form.get('accion')

    if not accion:
        flash('Error: El campo "Acción" es obligatorio.')
        return redirect('/')  # Redirige de nuevo a la página principal

    destino = request.form.get('destino', '')
    dirigencia = request.form.get('dirigencia', '')
    hora_evento = request.form.get('hora_evento')
    fecha_evento = request.form.get('fecha_evento')

    # Si se proporciona hora_evento y fecha_evento, se usan, si no, se usa la hora y fecha del servidor
    if hora_evento and fecha_evento:
        hora = hora_evento
        fecha = fecha_evento
    else:
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

    flash('Registro guardado exitosamente.') # Agrega un mensaje de éxito
    return redirect('/')


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

    if not (0 <= indice < len(historial)): #verifica que el indice sea valido
        flash('Error: Índice de registro inválido.')
        return redirect('/')

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
        flash('Registro editado exitosamente.')
        return redirect('/')

    # Obtener el registro para mostrar en el formulario
    registro = historial[indice]
    return render_template("editar.html", registro=registro, indice=indice)

if __name__ == '__main__':
    app.run(debug=True)
