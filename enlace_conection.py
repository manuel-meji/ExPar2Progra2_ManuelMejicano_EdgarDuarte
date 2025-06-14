import mysql.connector
from mysql.connector import Error
import google.generativeai as genai

# Configurar la API de Gemini
genai.configure(api_key='AIzaSyBhvhVpbSJ8H5kAap-wELrXLhlzyBN8q48')
model = genai.GenerativeModel('gemini-1.5-flash')

def conectar_y_obtener_datos():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Manuel2004", 
            database="proyecto1"
        )
        if conexion.is_connected():
            print("✅ Conexión exitosa a la base de datos")

            cursor = conexion.cursor()
            cursor.execute("SELECT fecha, COUNT(*) FROM ingresos GROUP BY fecha;")
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()

            # Formatear resultados para incluir en el contexto
            datos = "\n".join([f"{fecha}: {cantidad}" for fecha, cantidad in resultados])
            return datos
    except Error as e:
        print(f"❌ Error: {e}")
        return None

# Obtener datos de la base de datos
contexto_datos = conectar_y_obtener_datos()

if contexto_datos:
    print("\n📊 Datos cargados desde la base de datos:\n")
    print(contexto_datos)

    print("\n🧠 Puedes hacer preguntas sobre los datos. Escribe 'salir' para terminar.\n")

    chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": [f"Aquí están los datos de ingresos por fecha:\n\n{contexto_datos}\n\nQuiero que me ayudes a analizarlos."]
        },
        {
            "role": "model",
            "parts": ["¡Claro! Estoy listo para ayudarte a analizarlos. Puedes preguntarme lo que quieras sobre los ingresos."]
        }
    ])

    while True:
        pregunta = input("Tú: ")
        if pregunta.strip().lower() == "salir":
            print("👋 Saliendo del chat...")
            break

        respuesta = chat.send_message(pregunta)
        print("\nGemini:", respuesta.text, "\n")
else:
    print("⚠️ No se pudo obtener información de la base de datos.")
