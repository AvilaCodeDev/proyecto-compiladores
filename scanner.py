#Este scanner solo lee fórmulas matemáticas

class Token:
    def __init__(self, type_, lexema):
        self.type = type_
        self.lexema = lexema
    
    def __repr__(self):
        return f"Token({self.type}, '{self.lexema}')"
    
class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens= []
        self.current=0
    
    def scan(self):
        try:
            while not self.is_at_end():
                char=self.advance()

                #para ignorar espacios
                if char.isspace():
                    continue

                #para operadores
                if char in "+-*/%=(),;":
                    token_map = {
                        '+': 'MAS',
                        '-': 'MENOS',
                        '*': 'MULT',
                        '/': 'DIV',
                        '%': 'MOD',
                        '=': 'IGUAL',
                        '(': 'PARENTESIS_ABRIR',
                        ')': 'PARENTESIS_CERRAR',
                        ',': 'COMA',
                        ';': 'PUNTO_COMA'
                    }
                    self.tokens.append(Token(token_map[char], char))
                    continue

                #para numeros
                if char.isdigit():
                    self.tokens.append(self.number(char))
                    continue

                #para palabras reservadas
                if char.isalpha() or char == "_":
                    self.tokens.append(self.identifier(char))
                    continue

                #para cadenas
                if char == '"':
                    tok, error = self.string()
                    if error:
                        return None, error
                    self.tokens.append(tok)
                    continue

                #cualquier otro caracter es un error
                return None, f"Error lexico: caracter inesperado '{char}'"
            
            #token de salida
            self.tokens.append(Token("EOF", ""))

            return self.tokens, None
        
        except Exception as e:
            return None, f"Error lexico inesperado: {str(e)}"
        
    #----------
    def is_at_end(self):
        return self.current >= len(self.source)
    
    def advance(self):
        ch=self.source[self.current]
        self.current +=1
        return ch
        
    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]
    
    def number(self,start):
        lexema=start
        while not self.is_at_end() and self.peek().isdigit():
            lexema += self.advance()

        return Token("NUMBER", lexema)
    
    def identifier(self, start):
        lexema = start
        while not self.is_at_end() and (self.peek().isalnum() or self.peek() == "_"):
            lexema += self.advance()
        
        if lexema == "null":
            return Token("NULL", lexema)
        
        return Token("ID", lexema)
    
    def string(self):
        lexema=""

        while not self.is_at_end() and self.peek() != '"':
            lexema +=self.advance()

        if self.is_at_end():
            return None, "Error lexico: cadena no cerrada"
        self.advance()

        return Token("STRING", lexema), None
        
    
    