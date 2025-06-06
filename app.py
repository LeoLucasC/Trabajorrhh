import os
import sqlite3
import PyPDF2
from flask import Flask, request, render_template, redirect, url_for
import joblib

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la base de datos SQLite
DATABASE = 'database.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cargo TEXT NOT NULL
            )
        ''')
        conn.commit()

# Inicializar la base de datos al arrancar la aplicación
init_db()

# Cargar el modelo preentrenado
model = joblib.load('modelo_mejorado.pkl')

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
    if request.method == 'POST':
        if 'files' in request.files:
            files = request.files.getlist('files')
            name = request.form['name']
            cargo = request.form['cargo']
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

                # Clasificar el CV
                prediction = model.predict([text])[0]
                probabilities = model.predict_proba([text])[0]
                areas = model.classes_
                results = {area: round(prob * 100, 2) for area, prob in zip(areas, probabilities)}
                results_list.append({'prediction': prediction, 'results': results})

            if not results_list:
                return render_template('welcome.html', name=name, cargo=cargo, error="No se procesaron archivos válidos.")
            
            return render_template('welcome.html', name=name, cargo=cargo, results_list=results_list)

    personal_id = request.args.get('personal_id')
    if not personal_id:
        return redirect(url_for('index'))
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, cargo FROM personal WHERE id = ?', (personal_id,))
        personal = cursor.fetchone()
    
    if not personal:
        return redirect(url_for('index'))
    
    name, cargo = personal
    return render_template('welcome.html', name=name, cargo=cargo)

if __name__ == '__main__':
    app.run(debug=True)