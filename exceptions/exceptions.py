from dfa.token import Token
class EstadoNoExistente(Exception):
    def __init__(self):
        self.message = "El estado no pertenece al conjunto de estados del automata!"
        super().__init__(self.message)
class ArchivoVacio(Exception):
    def __init__(self):
        self.message = "el archivo esta vacio!"
        super().__init__(self.message)

class EstadoSiguienteNoExiste(Exception):
    def __init__(self):
        self.message = "Simbolo no tiene estado siguiente. Token incorrecto"
        super().__init__(self.message)

class LexicoTokenIncorrecto(Exception):
    def __init__(self, cordinates: tuple[str, str], actual : str):
        self.message = f"Error lexico: token incorrecto {actual} en fila {cordinates[0]}, columna {cordinates[1]}"
        super().__init__(self.message)

class SemanticoTokenFaltante(Exception):
    def __init__(self, token_actual : Token, tokens : list[Token]):
        self.message = f"Error sintactico: {tokens} faltante detectado antes de <{token_actual.lexem}> {token_actual.initial_coordinates}"
        super().__init__(self.message)

class SemanticoTokenIncorrecto(Exception):
    def __init__(self, tokens : list[Token], token_actual : Token):
        self.message = f"Error sintactico con <{token_actual.lexem}>: se espera {tokens} entre {token_actual.initial_coordinates} y {token_actual.final_coordinates}"
        super().__init__(self.message)

class LexicoNoTokenSiguiente(Exception):
    def __init__(self):
        self.message = "Error lexico: no hay token siguiente!"
        super().__init__(self.message)

class SemanticoProgramaIncorrecto(Exception):
    def __init__(self, token : Token):
        self.message = f"Error semantico: fin del programa alcanzado y token encontrado: {token}"
        super().__init__(self.message)

class SemanticoSimboloNoDeclarado(Exception):
    def __init__(self, token : Token):
        self.message = f"Error semantico: {token} no declarado."
        super().__init__(self.message)