import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from nltk.corpus import stopwords
import nltk

# Descargar stopwords si no están disponibles
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Lista de stopwords en español
spanish_stopwords = stopwords.words('spanish')

# Lista de archivos CSV
csv_files = [
    "dataset_training_administration.csv",
    "dataset_training_enfermeria.csv",
    "dataset_training_limpieza.csv",
    "dataset_training_tecnica_enfermera.csv",
    "dataset_training_seguridad.csv"
]

def cargar_datos():
    dataframes = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if not {'texto', 'etiqueta'}.issubset(df.columns):
                print(f"⚠️ Archivo {file} no tiene las columnas requeridas")
                continue
            dataframes.append(df)
            print(f"✓ {file} cargado ({len(df)} muestras)")
        except Exception as e:
            print(f"❌ Error en {file}: {str(e)}")
    
    if not dataframes:
        raise ValueError("No hay datos válidos para entrenar.")
    
    df_combined = pd.concat(dataframes, ignore_index=True)
    return df_combined.dropna().drop_duplicates()

def crear_modelo():
    return make_pipeline(
        TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words=spanish_stopwords,  # Usamos la lista descargada
            lowercase=True,
            min_df=3  # Ignora términos que aparecen en menos de 3 documentos
        ),
        MultinomialNB(alpha=0.1)
    )

def entrenar_y_evaluar():
    # Cargar datos
    df = cargar_datos()
    print(f"\n📊 Dataset final: {len(df)} muestras")
    print("📌 Distribución de clases:")
    print(df['etiqueta'].value_counts())

    # Balancear clases (opcional)
    # df = df.groupby('etiqueta').apply(lambda x: x.sample(200)).reset_index(drop=True)

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        df['texto'], df['etiqueta'], test_size=0.2, random_state=42, stratify=df['etiqueta']
    )

    # Entrenar modelo
    model = crear_modelo()
    model.fit(X_train, y_train)

    # Evaluación
    y_pred = model.predict(X_test)
    print("\n📝 Reporte de clasificación:")
    print(classification_report(y_test, y_pred))

    # Guardar modelo
    joblib.dump(model, "modelo_mejorado.pkl")
    print("\n✅ Modelo guardado como 'modelo_mejorado.pkl'")

if __name__ == "__main__":
    entrenar_y_evaluar()