from parser import parser

while True:
    try:
        s = input('Ingrese una sentencia CRUD en español: ')
    except EOFError:
        break
    parser.parse(s)
