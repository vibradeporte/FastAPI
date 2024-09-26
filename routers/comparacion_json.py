import json
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Query, Depends
from jwt_manager import JWTBearer

comparacion_router = APIRouter()

#Consultar en cuales cursos esta registrado un usuario.
@comparacion_router.get("/comparacion/", tags=['extra'], status_code=200, dependencies=[Depends(JWTBearer())])
def comparacion(json_1: str, json_2: str):

    if isinstance(json_1, str):
        json_1 = json.loads(json_1)  

    if isinstance(json_2, str):
        json_2 = json.loads(json_2)  

    # Función para eliminar solo los espacios en cadenas de texto
    def clean_text(text):
        if isinstance(text, str):
            # Eliminar solo los espacios en blanco
            return text.replace(' ', '')  # Remover solo los espacios
        return text  # Si es un número, devolverlo tal cual
    
    def convert_if_numeric(value):
        try:
            # Intentar convertir a entero
            return int(value)
        except ValueError:
            # Si falla, devolver el valor original (es una cadena)
            return value

    # 1. Extraer los valores "value" del primer JSON y limpiarlos
    valores_json_1 = []
    
    for item in json_1:
        row = item['row']
        # Calcular dinámicamente cuántas columnas hay (cuántas claves existen)
        num_columns_per_group = len(row.keys())  # El número de claves en cada fila
        # Iterar sobre todas las claves dinámicas dentro de 'row' (como a, b, c, d, etc.)
        for key in sorted(row.keys()):  # Ordenar por las claves (a, b, c, ...)
            valor = clean_text(row[key]['value'])
            valor = convert_if_numeric(valor)
            valores_json_1.append(valor)
    
    # 2. Agrupar los valores de valores_json_1 en tuplas basadas en el número de claves dinámicas
    valores_json_1_tuplas = [
        tuple(valores_json_1[i:i+num_columns_per_group])
        for i in range(0, len(valores_json_1), num_columns_per_group)
    ]

    print(valores_json_1_tuplas)

    # 3. Acceder al objeto dentro del array y luego a la clave "data" del segundo JSON
    valores_json_2 = []
    for item in json_2[0]['data']:  # Accedemos al primer elemento del array y luego a "data"
        # Convertimos los valores del diccionario en una tupla y limpiamos los textos
        tupla = tuple(clean_text(value) for value in item.values())
        valores_json_2.append(tupla)

    print(valores_json_2)
    # 3. Comparar los dos conjuntos de datos
    if set(valores_json_1_tuplas) == set(valores_json_2):
        return {"resultado": "coinciden"}
    else:
        return {"resultado": "no coinciden"}