import joblib
import pandas as pd
from colorama import Fore, Style, init
from nltk.corpus import stopwords
import nltk

# Inicializar colorama
init(autoreset=True)

# Cargar stopwords en español
try:
    spanish_stopwords = stopwords.words('spanish')
except LookupError:
    nltk.download('stopwords')
    spanish_stopwords = stopwords.words('spanish')

def cargar_modelo():
    try:
        model = joblib.load("modelo_mejorado.pkl")
        print(Fore.GREEN + "✓ Modelo cargado correctamente")
        return model
    except Exception as e:
        print(Fore.RED + f"Error al cargar el modelo: {e}")
        return None

def predecir_con_umbral(modelo, texto, umbral=0.6):
    try:
        probas = modelo.predict_proba([texto])[0]
        clase_predicha = modelo.classes_[probas.argmax()]
        confianza = probas.max()
        
        if confianza < umbral:
            return "Rechazado (Confianza baja)", probas, False
        return clase_predicha, probas, True
    except Exception as e:
        print(Fore.RED + f"Error en predicción: {e}")
        return None, None, False

def mostrar_resultados(modelo, texto, real, pred, probas, es_valido):
    print(f"\n{Fore.CYAN}CV analizado:{Style.RESET_ALL} {texto}")
    print(f"{Fore.YELLOW}Área esperada:{Style.RESET_ALL} {real}")
    
    if not es_valido:
        print(Fore.RED + "✖ Predicción no válida (confianza baja)")
    else:
        color = Fore.GREEN if pred == real else Fore.RED
        print(f"{color}Área predicha:{Style.RESET_ALL} {pred}")
    
    print("\nProbabilidades:")
    for area, prob in sorted(zip(modelo.classes_, probas), 
                          key=lambda x: x[1], 
                          reverse=True):
        pct = f"{prob:.2%}"
        if area == real and es_valido:
            print(f"{Fore.GREEN}  - {area}: {pct}{Style.RESET_ALL}")
        elif area == pred and es_valido:
            print(f"{Fore.YELLOW}  - {area}: {pct}{Style.RESET_ALL}")
        else:
            print(f"  - {area}: {pct}")

def main():
    modelo = cargar_modelo()
    if not modelo:
        return

    # Ejemplos de prueba (puedes modificarlos)
    ejemplos = [
        {
            "texto": "Gestión de equipos administrativos y control presupuestario en clínica privada",
            "real": "Administración"
        },
        {
            "texto": "Cuidado de pacientes geriátricos y administración de medicamentos",
            "real": "Enfermería"
        },
        {
            "texto": "Limpieza de quirófanos y manejo de desinfectantes especializados",
            "real": "Limpieza"
        },
        {
            "texto": "Asistencia en cirugías menores y toma de constantes vitales",
            "real": "Técnica Enfermera"
        },
        {
            "texto": "Vigilancia de instalaciones y manejo de sistemas de seguridad",
            "real": "Seguridad"
        }
    ]

    for ejemplo in ejemplos:
        pred, probas, valido = predecir_con_umbral(modelo, ejemplo["texto"])
        if pred is not None:
            mostrar_resultados(
                modelo,
                ejemplo["texto"],
                ejemplo["real"],
                pred,
                probas,
                valido
            )

if __name__ == "__main__":
    main()