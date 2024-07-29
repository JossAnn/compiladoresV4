import ply.yacc as yacc
from lexer import tokens

def p_statement_select(p):
    'statement : SELECT ID FROM ID WHERE expression'
    print("SELECT statement:", p[2], "FROM", p[4], "WHERE", p[6])

def p_statement_insert(p):
    'statement : INSERT INTO ID VALUES expression'
    print("INSERT statement:", "INTO", p[3], "VALUES", p[5])

def p_statement_update(p):
    'statement : UPDATE ID SET ID VALUES expression'
    print("UPDATE statement:", p[2], "SET", p[4], "VALUES", p[6])

def p_statement_delete(p):
    'statement : DELETE FROM ID WHERE expression'
    print("DELETE statement:", "FROM", p[3], "WHERE", p[5])

def p_expression(p):
    '''expression : comparison_expression
                  | value_expression'''
    p[0] = p[1]

def p_comparison_expression(p):
    '''comparison_expression : expression GT expression'''
    p[0] = (p[1], '>', p[3])

def p_value_expression(p):
    '''value_expression : ID
                         | NUMBER
                         | STRING'''
    p[0] = p[1]

def p_error(p):
    if p:
        print("Error de sintaxis en el token:", p.type)
    else:
        print("Error de sintaxis en la entrada")

# Construir el parser
parser = yacc.yacc()
