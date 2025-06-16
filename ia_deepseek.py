import mysql.connector
from mysql.connector import Error
import requests
import json

# Configuración de DeepSeek - ¡OBTÉN TU API KEY GRATUITA!
DEEPSEEK_API_KEY = "sk-538fd21730874281b167c230cd3b3984"  # 👈 Reemplaza ESTO con tu API key real
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"

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

            columnas = [col[0] for col in cursor.description]

            cursor.close()
            conexion.close()

            datos_formateados = []
            for fila in resultados:
                fila_dict = dict(zip(columnas, fila))
                texto = (f"ID: {fila_dict['id']} | Cédula: {fila_dict['cedula']} | "
                         f"Fecha: {fila_dict['fecha']} | Hora: {fila_dict['hora']} | "
                         f"Motivo: {fila_dict['motivo'] or 'N/A'} | Guarda: {fila_dict['nombre_usuario_guarda']} | "
                         f"Placa: {fila_dict['placa_vehiculo'] or 'N/A'} | Tipo: {fila_dict['tipoIngreso']}")
                datos_formateados.append(texto)

            return "\n".join(datos_formateados)

    except Error as e:
        print(f"❌ Error de base de datos: {e}")
        return None

def enviar_mensaje_deepseek(messages):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as err:
        print(f"❌ Error de API (HTTP {err.response.status_code}): {err.response.text}")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
    return None

# Verificar API key antes de continuar
if DEEPSEEK_API_KEY == "tu_api_key_aqui":
    print("\n⚠️ ERROR CRÍTICO: No has configurado tu API key de DeepSeek")
    print("Por favor visita: https://platform.deepseek.com/ para obtener una API key gratuita")
    print("Reemplaza 'tu_api_key_aqui' en el código con tu clave real\n")
    exit()

# Obtener datos de la base de datos
contexto_datos = conectar_y_obtener_datos()

if contexto_datos:
    print("\n📊 Datos cargados desde la base de datos:\n")
    print(contexto_datos)

    # Configurar historial inicial
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un analista de registros de acceso. Los datos contienen: "
                "ID, cédula, fecha, hora, motivo, guarda responsable, placa de vehículo y tipo de ingreso. "
                "Tipos de ingreso: Funcionario, Externo, VehiculoExterno. "
                "Analiza patrones, irregularidades y responde preguntas específicas."
            )
        },
        {
            "role": "user",
            "content": f"Estos son los registros de acceso:\n\n{contexto_datos}\n\n¿Qué observaciones destacadas encuentras?"
        }
    ]

    # Obtener primera respuesta analítica
    print("\n🧠 Consultando a DeepSeek para análisis inicial...")
    respuesta_inicial = enviar_mensaje_deepseek(messages)
    
    if respuesta_inicial:
        print("\n🤖 DeepSeek:", respuesta_inicial, "\n")
        messages.append({"role": "assistant", "content": respuesta_inicial})
    else:
        print("⚠️ No se pudo obtener respuesta inicial")
    
    print("\n💬 Puedes hacer preguntas sobre los datos. Escribe 'salir' para terminar.\n")

    while True:
        pregunta = input("Tú: ")
        if pregunta.strip().lower() == 'salir':
            print("👋 Saliendo del chat...")
            break

        messages.append({"role": "user", "content": pregunta})
        
        respuesta = enviar_mensaje_deepseek(messages)
        if respuesta:
            print("\n🤖 DeepSeek:", respuesta, "\n")
            messages.append({"role": "assistant", "content": respuesta})
        else:
            print("⚠️ No se recibió respuesta. Intenta reformular tu pregunta")
else:
    print("⚠️ No se pudo obtener información de la base de datos.")