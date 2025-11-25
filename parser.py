import sys #--Sirve para imprimir mensajes de diagnóstico de consola

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.indent_level = 0
        self.indent_char = "   " # Usamos 3 espacios para la indentación

    # --- Herramientas Básicas ---

    def peek(self):
        """
        Devuelve el token actual (lookahead) sin consumir ni avanzar el puntero.
        Es vital para la toma de decisiones del parser.
        """
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        # Crear un token EOF simple si no hay más tokens
        class EOFToken:
            def __init__(self):
                self.type = 'EOF'
                self.lexema = ''
        return EOFToken()

    def advance(self):
        """
        Consume el token actual y avanza el puntero al siguiente token.
        Se llama *después* de que se ha confirmado que el token actual es correcto.
        """
        self.current_token_index += 1

    def match(self, expected_type):
        """
        Operación fundamental del parser. Verifica si el token actual coincide con el 
        tipo esperado y, si coincide, lo consume (avanza el puntero). Si falla, lanza un error sintáctico.
        """
        current = self.peek()
        if current.type == expected_type:
            self.advance()
            # Impresión de confirmación para la traza
            print(f"{self.indent_char * self.indent_level}MATCH: {expected_type} ('{current.lexema or current.type}')")
            return current
        else:
            # Reporte de error
            error_msg = (
                f"Error de Sintaxis: Se esperaba '{expected_type}' pero se encontró '{current.type}'"
            )
            print(error_msg, file=sys.stderr)
            raise SyntaxError(error_msg)

    def trace(self, non_terminal):
        """
        Marca la entrada a una regla de producción. Imprime el mensaje y aumenta la sangría.
        Muestra que el parser entra a analizar una nueva estructura (recursión hacia abajo).
        """
        print(f"{self.indent_char * self.indent_level} Analizando {non_terminal}")
        self.indent_level += 1 # Aumenta la profundidad de la traza

    def untrace(self, non_terminal):
        """
        Marca la salida de una regla de producción. Disminuye la sangría.
        Muestra que el parser terminó de reconocer una estructura (recursión hacia arriba).
        """
        self.indent_level -= 1 # Disminuye la profundidad de la traza
        print(f"{self.indent_char * self.indent_level} Fin {non_terminal}")

    # --- Funciones de Producción  ---

    def statement(self):
        # STATEMENT -> EXPRESSION SEMICOLON_OPC
        # Regla de inicio: Toda sentencia es una EXPRESSION seguida de un PUNTO_COMA opcional.
        self.trace("STATEMENT")
        self.expression()
        self.semicolon_opc()
        self.untrace("STATEMENT")
    
    def semicolon_opc(self):
        # SEMICOLON_OPC -> ; | ε (vacío)
        # Maneja el punto y coma opcional. Usa peek para decidir si consumir o tomar ε.
        self.trace("SEMICOLON_OPC")
        if self.peek().type == 'PUNTO_COMA':
            self.match('PUNTO_COMA') # Consume el ';'
        # Si no es PUNTO_COMA, se asume la producción vacía (ε) y no se hace nada.
        self.untrace("SEMICOLON_OPC")

    def expression(self):
        # EXPRESSION -> ASSIGNMENT
        # La regla principal de expresión es, en este lenguaje, una asignación.
        self.trace("EXPRESSION")
        self.assignment()
        self.untrace("EXPRESSION")

    def assignment(self):
        # ASSIGNMENT -> TERM ASSIGNMENT_OPC
        # La asignación permite (TERM) seguido de (= EXPRESSION) opcional.
        self.trace("ASSIGNMENT")
        self.term()
        self.assignment_opc()
        self.untrace("ASSIGNMENT")

    def assignment_opc(self):
        # ASSIGNMENT_OPC -> = EXPRESSION | ε
        # Maneja el operador de asignación '=' opcional.
        self.trace("ASSIGNMENT_OPC")
        if self.peek().type == 'IGUAL':
            self.match('IGUAL') # Consume el '='
            self.expression()   # Llama recursivamente a EXPRESSION para el valor a asignar
        # Si no es IGUAL, se asume ε (ej. si la expresión es solo `10 + 5`)
        self.untrace("ASSIGNMENT_OPC")

    def term(self):
        # TERM -> FACTOR TERM'
        # Regla para operadores de SUMA/RESTA (baja precedencia). 
        # Llama a FACTOR (mayor precedencia) y luego a TERM' para manejar la repetición.
        self.trace("TERM (Suma/Resta)")
        self.factor()
        self.term_prime()
        self.untrace("TERM (Suma/Resta)")

    def term_prime(self):
        # TERM' -> + TERM | - TERM | ε
        # Implementa la recursión a la derecha para manejar expresiones como a + b - c.
        self.trace("TERM_PRIME")
        token_type = self.peek().type
        if token_type in ['MAS', 'MENOS']: # Considera ambos operadores + y - según la gramática
            self.match(token_type)
            self.term() # Vuelve a llamar a TERM para el resto de la expresión
        # Si no es + ni -, se asume ε.
        self.untrace("TERM_PRIME")

    def factor(self):
        # FACTOR -> UNARY FACTOR'
        # Regla para operadores de MULTIPLICACIÓN/DIVISIÓN (precedencia media).
        # Llama a UNARY (mayor precedencia) y luego a FACTOR' para manejar la repetición.
        self.trace("FACTOR (Mult/Div)")
        self.unary()
        self.factor_prime()
        self.untrace("FACTOR (Mult/Div)")

    def factor_prime(self):
        # FACTOR' -> / FACTOR | * FACTOR | % FACTOR | ε
        # Maneja la repetición de operadores de Multiplicación/División/Módulo.
        self.trace("FACTOR_PRIME")
        token_type = self.peek().type
        if token_type in ['DIV', 'MULT', 'MOD']:
            self.match(token_type) # Consume el operador
            self.factor()          # Vuelve a llamar a FACTOR
        # Si no es un operador, se asume ε.
        self.untrace("FACTOR_PRIME")
    
    def unary(self):
        # UNARY -> - UNARY | CALL
        # Nivel de operador UNARIO (signo negativo). Tiene la mayor precedencia.
        self.trace("UNARY")
        if self.peek().type == 'MENOS':
            self.match('MENOS') # Consume el signo '-'
            self.unary()        # Recursión a la derecha para manejar múltiples signos (e.g., --x)
        else:
            self.call() # Si no hay signo, delega a CALL (llamada a función o valor primario)
        self.untrace("UNARY")

    def call(self):
        # CALL -> PRIMARY CALL'
        # Nivel de LLAMADA A FUNCIÓN. Asegura que la llamada ocurre después de reconocer el nombre (PRIMARY).
        self.trace("CALL")
        self.primary()
        self.call_prime() # Llama a CALL_PRIME para ver si hay paréntesis de llamada
        self.untrace("CALL")

    def call_prime(self):
        # CALL' -> (ARGUMENTS) | ε
        # Maneja la parte opcional de la llamada: los paréntesis y los argumentos.
        self.trace("CALL_PRIME")
        if self.peek().type == 'PARENTESIS_ABRIR':
            self.match('PARENTESIS_ABRIR')
            self.arguments()            # Analiza la lista de argumentos
            self.match('PARENTESIS_CERRAR')
        # Si no hay '(', se asume ε (la expresión es solo un valor primario, no una llamada).
        self.untrace("CALL_PRIME")

    def primary(self):
        # PRIMARY -> null | number | string | id | (EXPRESSION)
        # Nivel de máxima precedencia: Valores atómicos o expresiones entre paréntesis.
        self.trace("PRIMARY")
        token_type = self.peek().type
        
        # Opción 1: Valores literales o Identificadores
        if token_type in ['NULL', 'NUMBER', 'STRING', 'ID']:
            self.match(token_type) # Consume el valor (ej. '10', 'x', 'null')
        # Opción 2: Expresión entre paréntesis (para forzar precedencia)
        elif token_type == 'PARENTESIS_ABRIR':
            self.match('PARENTESIS_ABRIR')
            self.expression() # Analiza la expresión interna
            self.match('PARENTESIS_CERRAR')
        else:
            # Falla si no es ninguna opción válida.
            raise SyntaxError(f"Error: Se esperaba un valor PRIMARY, pero se encontró {token_type}")
        self.untrace("PRIMARY")

    def arguments(self):
        # ARGUMENTS -> EXPRESSION ARGUMENTS' | ε
        # Inicia el análisis de la lista de argumentos dentro de una llamada a función.
        self.trace("ARGUMENTS")
        # Si no hay paréntesis de cierre, se espera al menos una EXPRESSION.
        if self.peek().type != 'PARENTESIS_CERRAR':
            self.expression()
            self.arguments_prime() # Llama a la prima para buscar más argumentos con coma
        # Si el lookahead es PARENTESIS_CERRAR, asume ε (lista de argumentos vacía).
        self.untrace("ARGUMENTS")
    
    def arguments_prime(self):
        # ARGUMENTS' -> , EXPRESSION ARGUMENTS' | ε
        # Maneja la repetición de argumentos separados por coma (e.g., arg1, arg2, ...).
        self.trace("ARGUMENTS_PRIME")
        if self.peek().type == 'COMA':
            self.match('COMA')
            self.expression()
            self.arguments_prime() # Recursión para seguir buscando más argumentos
        # Si no hay coma, asume ε (fin de la lista de argumentos).
        self.untrace("ARGUMENTS_PRIME")

    def parse(self):
        """Función principal que inicia el análisis sintáctico del código fuente."""
        print("\n--- INICIO DEL ANÁLISIS SINTÁCTICO ---")
        self.statement() # Inicia el análisis desde la regla más alta
        
        # Verificación final de EOF
        if self.peek().type != 'EOF':
            # Si hay tokens restantes, significa que el código está incompleto o malformado.
            raise SyntaxError("Error: El código no fue completamente analizado al final.")
        
        print("\nAnálisis Sintáctico Exitoso: La entrada es válida según la gramática.")