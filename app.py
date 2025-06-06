import os
import sqlite3
import PyPDF2
import re
import json
from flask import Flask, request, render_template, redirect, url_for
import joblib

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la base de datos SQLite
DATABASE = 'database.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Tabla para usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cargo TEXT NOT NULL
            )
        ''')
        # Tabla para resultados de CVs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cv_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personal_id INTEGER NOT NULL,
                cv_text TEXT,
                prediction TEXT NOT NULL,
                probabilities TEXT NOT NULL,
                phone_number TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (personal_id) REFERENCES personal (id)
            )
        ''')
        conn.commit()

# Inicializar la base de datos al arrancar la aplicación
init_db()

# Cargar el modelo preentrenado
try:
    model = joblib.load('modelo_mejorado.pkl')
except FileNotFoundError:
    print("Error: El archivo 'modelo_mejorado.pkl' no se encuentra. Asegúrate de entrenar el modelo primero.")
    model = None

@app.route('/')
def index():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, cargo FROM personal')
        personal_list = cursor.fetchall()
    return render_template('index.html', personal_list=personal_list)

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/add_personal', methods=['POST'])
def add_personal():
    name = request.form['name']
    cargo = request.form['cargo']
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO personal (name, cargo) VALUES (?, ?)', (name, cargo))
        conn.commit()
    
    return redirect(url_for('index'))

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    personal_id = request.args.get('personal_id')
    if not personal_id:
        return redirect(url_for('index'))
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, cargo FROM personal WHERE id = ?', (personal_id,))
        personal = cursor.fetchone()
    
    if not personal:
        return redirect(url_for('index'))
    
    # Desempaquetar solo name y cargo, usando el personal_id ya obtenido
    name, cargo = personal

    if request.method == 'POST':
        if 'files' in request.files:
            files = request.files.getlist('files')
            results_list = []

            for file in files:
                if file.filename == '':
                    continue
                
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                except Exception as e:
                    return render_template('welcome.html', name=name, cargo=cargo, error="Error al leer un PDF. Asegúrate de que todos sean archivos válidos.")

                # Extraer número de celular de 9 dígitos
                phone_number = None
                phone_match = re.search(r'\b\d{9}\b', text)
                if phone_match:
                    phone_number = phone_match.group(0)

                # Clasificar el CV
                if model is None:
                    return render_template('welcome.html', name=name, cargo=cargo, error="Modelo no cargado. Entrena el modelo primero.")
                
                prediction = model.predict([text])[0]
                probabilities = model.predict_proba([text])[0]
                areas = model.classes_
                results = {area: round(prob * 100, 2) for area, prob in zip(areas, probabilities)}

                # Guardar en la base de datos
                with sqlite3.connect(DATABASE) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO cv_results (personal_id, cv_text, prediction, probabilities, phone_number)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (personal_id, text[:1000], prediction, json.dumps(results), phone_number))
                    conn.commit()

                results_list.append({
                    'prediction': prediction,
                    'results': results,
                    'phone_number': phone_number
                })

            if not results_list:
                return render_template('welcome.html', name=name, cargo=cargo, error="No se procesaron archivos válidos.")

    # Recuperar los resultados previos para este personal
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT prediction, probabilities, phone_number, timestamp FROM cv_results WHERE personal_id = ?', (personal_id,))
        previous_results = cursor.fetchall()
        previous_results = [
            {
                'prediction': pred,
                'results': json.loads(probs),
                'phone_number': phone,
                'timestamp': ts
            }
            for pred, probs, phone, ts in previous_results
        ]

        # Calcular estadísticas
        cursor.execute('SELECT COUNT(*) FROM cv_results WHERE personal_id = ?', (personal_id,))
        cv_count = cursor.fetchone()[0]
        # Calcular match_count iterando sobre los resultados
        match_count = sum(1 for result in previous_results if result['results'][result['prediction']] > 70)

    return render_template('welcome.html', name=name, cargo=cargo, results_list=results_list if 'results_list' in locals() else [], previous_results=previous_results, cv_count=cv_count, match_count=match_count)

if __name__ == '__main__':
    app.run(debug=True)