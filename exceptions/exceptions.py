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

class TokenIncorrecto(Exception):
    def __init__(self, cordinates: tuple[str, str]):
        self.message = f"Token incorrecto en fila {cordinates[0]}, columna {cordinates[1]}"
        super().__init__(self.message)