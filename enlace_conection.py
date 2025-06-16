import mysql.connector
from mysql.connector import Error
import google.generativeai as genai

# Configurar la API de Gemini
genai.configure(api_key='AIzaSyBhvhVpbSJ8H5kAap-wELrXLhlzyBN8q48')  # Reemplaza TU_API_KEY si aún no lo has hecho
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
            cursor.execute("SELECT * FROM ingresos ORDER BY fecha, hora;")
            resultados = cursor.fetchall()

            columnas = [col[0] for col in cursor.description]  # Obtener nombres de columnas

            cursor.close()
            conexion.close()

            # Formatear los resultados como texto legible
            datos_formateados = []
            for fila in resultados:
                fila_dict = dict(zip(columnas, fila))
                texto = (f"ID: {fila_dict['id']} | "
                         f"Cédula: {fila_dict['cedula']} | "
                         f"Fecha: {fila_dict['fecha']} | "
                         f"Hora: {fila_dict['hora']} | "
                         f"Motivo: {fila_dict['motivo'] or 'N/A'} | "
                         f"Guarda: {fila_dict['nombre_usuario_guarda']} | "
                         f"Placa: {fila_dict['placa_vehiculo'] or 'N/A'} | "
                         f"Tipo: {fila_dict['tipoIngreso']}")
                datos_formateados.append(texto)

            return "\n".join(datos_formateados)

    except Error as e:
        print(f"❌ Error: {e}")
        return None

# Obtener datos
contexto_datos = conectar_y_obtener_datos()

if contexto_datos:
    print("\n📊 Datos cargados desde la base de datos:\n")
    print(contexto_datos)

    print("\n🧠 Puedes hacer preguntas sobre los datos. Escribe 'salir' para terminar.\n")

    chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": [(
                "Aquí están los datos de ingresos registrados en la base de datos. "
                "Hay tres tipos de ingreso: 'Funcionario', 'Externo' y 'VehiculoExterno'. "
                "Cada registro contiene ID, cédula, fecha, hora, motivo de ingreso, nombre del guarda que aprobó, "
                "y si es un ingreso de vehículo externo o funcionario, también la placa del vehículo. "
                "Analiza esta información:\n\n"
                f"{contexto_datos}\n\n"
                "Quiero que me ayudes a analizarlos, encontrar patrones, cantidades, irregularidades u observaciones generales."
            )]
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
