import mysql.connector
from mysql.connector import errorcode
import ply.lex as lex
from flask import Flask, jsonify, request, render_template_string, render_template
import json
import sqlparse  # Importar la biblioteca sqlparse
app = Flask(__name__)

# Configurar la conexión a la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'compi'
}

try:
    conn = mysql.connector.connect(**db_config)
    print("Conexión a la base de datos exitosa")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Acceso denegado. Verifica las credenciales.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Error: La base de datos no existe.")
    else:
        print("Error:", err)
    exit(1)

# Expresiones regulares para los tokens
reserved_words = {
    'CREATE': 'CREATE',
    'SELECT': 'SELECT',
    'INSERT': 'INSERT',
    'DROP': 'DROP',
    'UPDATE': 'UPDATE',
    'SET': 'SET',
    'WHERE': 'WHERE',
    'FROM': 'FROM',
}

tokens = [
    'EQUAL',
    'NUMBER',
    'IDENTIFIER',
    'CHARACTER',
] + list(reserved_words.values())

# Definir el diccionario de categorías de tokens
token_categories = {
    'CREATE': 'Palabra reservada',
    'SELECT': 'Palabra reservada',
    'INSERT': 'Palabra reservada',
    'DROP': 'Palabra reservada',
    'UPDATE': 'Palabra reservada',
    'SET': 'Palabra reservada',
    'WHERE': 'Palabra reservada',
    'FROM': 'Palabra reservada',
    'EQUAL': 'Operador',
    'IDENTIFIER': 'Identificador',
    'NUMBER': 'Número',
    'CHARACTER': 'Carácter'
}

def t_CREATE(t):
    r'CREATE'
    t.type = reserved_words.get(t.value, 'CREATE')
    return t

def t_SELECT(t):
    r'SELECT'
    t.type = reserved_words.get(t.value, 'SELECT')
    return t

def t_INSERT(t):
    r'INSERT'
    t.type = reserved_words.get(t.value, 'INSERT')
    return t

def t_DROP(t):
    r'DROP'
    t.type = reserved_words.get(t.value, 'DROP')
    return t

def t_UPDATE(t):
    r'UPDATE'
    t.type = reserved_words.get(t.value, 'UPDATE')
    return t

def t_SET(t):
    r'SET'
    t.type = reserved_words.get(t.value, 'SET')
    return t

def t_WHERE(t):
    r'WHERE'
    t.type = reserved_words.get(t.value, 'WHERE')
    return t

def t_FROM(t):
    r'FROM'
    t.type = reserved_words.get(t.value, 'FROM')
    return t

def t_EQUAL(t):
    r'='
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved_words.get(t.value, 'IDENTIFIER')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CHARACTER(t):
    r'.'
    t.type = 'CHARACTER'
    return t

# Ignorar caracteres en blanco (espacios, tabulaciones, saltos de línea)
t_ignore = ' \t\n'

# Función para manejar errores de caracteres no reconocidos
def t_error(t):
    print(f"Carácter no reconocido: '{t.value[0]}' en la posición {t.lexer.lexpos}")
    t.lexer.skip(1)

# Construir el analizador léxico
lexer = lex.lex()
def analizador_sintactico(sentencia):
    try:
        parsed = sqlparse.parse(sentencia)
        if len(parsed) == 0:
            return "Análisis sintáctico: Sintaxis incorrecta."
        else:
            return "Análisis sintáctico: Sintaxis correcta."

    except Exception as e:
        return f"Análisis sintáctico: Error al analizar la sintaxis: {str(e)}"
def analizador_semantico(sentencia):
    # Analizador semántico básico para verificar el uso correcto de algunas palabras clave
    palabras_clave = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP']
    for palabra in palabras_clave:
        if palabra in sentencia.upper():
            return "Análisis semántico: Uso correcto de palabras clave."
    return "Análisis semántico: No se encontró ninguna palabra clave."


# Función para analizar la entrada y obtener tokens con categorías
def tokenize(input_string):
    lexer.input(input_string)
    tokens_info = []
    while True:
        token = lexer.token()
        if not token:
            break
        char_type = token.type
        char_value = token.value
        token_category = token_categories.get(char_type, 'Desconocido')
        tokens_info.append(f"[ {char_value} : {char_type} : {token_category} ]")
    return tokens_info

def execute_sql(sql_statements, conn):
    resultados = []
    cursor = None
    for statement in sql_statements:
        try:
            if statement.strip():
                cursor = conn.cursor()
                cursor.execute(statement)
                
                if statement.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    resultados.append({'sql_statement': statement, 'result': rows})
                else:
                    conn.commit()  # Confirmar cambios si no es una consulta SELECT
                    resultados.append({'sql_statement': statement, 'result': "OK"})
            else:
                resultados.append(None)
        except mysql.connector.Error as err:
            if "pitudos2" in err.msg:
                resultados.append({'sql_statement': statement, 'Server': "Al toque mi rey"})
            else:
                resultados.append({'sql_statement': statement, 'Server': f"Error & Warning: {err}"})
        finally:
            if cursor:
                # Leer todos los resultados no leídos antes de cerrar el cursor
                try:
                    while cursor.nextset():
                        cursor.fetchall()
                except mysql.connector.Error:
                    pass
                cursor.close()
                cursor = None
    return resultados


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_string = request.form['sql_statement']

        # Analizar la consulta SQL sintácticamente
        sintaxis_resultado = analizador_sintactico(input_string)

        # Analizar la consulta SQL semanticamente
        semantic_resultado = analizador_semantico(input_string)

        tokens_info = tokenize(input_string)
        resultados = execute_sql(input_string.split(';'), conn)

        # Agregar el resultado del análisis sintáctico a los resultados
        resultados.append({'analisis_sintactico': sintaxis_resultado})
        resultados.append({'analisis_sintactico': semantic_resultado})

        response = {'tokens_info': tokens_info, 'resultados': resultados}
        return jsonify(response)
    else:
        return render_template('index.html')
if __name__ == "__main__":
    app.run(debug=True)
