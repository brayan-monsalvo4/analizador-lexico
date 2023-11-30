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
        self.message = f"Error semantico: {token} no declarado, en {token.initial_coordinates} y {token.final_coordinates}."
        super().__init__(self.message)

class SemanticoTokensIncompatibles(Exception):
    def __init__(self, tokens : list[Token]):
        primero = tokens[0]
        ultimo = tokens[-1]
        self.message = f"Error semantico: {[token.lexem for token in tokens]} incompatibles, entre {primero.initial_coordinates} y {ultimo.final_coordinates}. "
        super().__init__(self.message)

class SemanticoSobreescribirConstante(Exception):
    def __init__(self, constante: Token):
        self.message = f"Error semantico: No se pueden sobreescribir constantes. Constante {constante.lexem}, en {constante.initial_coordinates} y {constante.final_coordinates} "
        super().__init__(self.message)


class SemanticoEstructuraIncorrecta(Exception):
    def __init__(self, estructura: Token):
        self.message = f"Error semantico: la estructura no posee un campo apuntador, en {estructura.initial_coordinates} y {estructura.final_coordinates}"
        super().__init__(self.message)

class SemanticoEstructuraApuntadorIncorrecto(Exception):
    def __init__(self, apuntador : Token):
        self.message = f"Error semantico: {apuntador.lexem} no es una estructura a la que apuntar, en {apuntador.initial_coordinates} y {apuntador.final_coordinates}"
        super().__init__(self.message)

class SemanticoSimboloYaExistente(Exception):
    def __init__(self, token : Token):
        self.message = f"Error semantico: {token.lexem} ya se encuentra declarado. En {token.initial_coordinates} y {token.final_coordinates}"  
        super().__init__(self.message)

class SemanticoEstructuraCamposIguales(Exception):
    def __init__(self, token : Token):
        self.message = f"Error semantico: Ambos campos se llaman igual. En {token.initial_coordinates} y {token.final_coordinates}"  
        super().__init__(self.message)


class SemanticoExpresionInvalida(Exception):
    def __init__(self, lista_valores : list[str], token : Token):
        self.message = f"Error semantico: la operacion entre {lista_valores} no esta definida para {token.lexem}, en {token.initial_coordinates} y {token.final_coordinates}."  
        super().__init__(self.message)

class SemanticoPunteroNulo(Exception):
    def __init__(self, token : Token):
        self.message = f"Error semantico: el puntero es nulo.{token.lexem}, en {token.initial_coordinates} y {token.final_coordinates}."  
        super().__init__(self.message)