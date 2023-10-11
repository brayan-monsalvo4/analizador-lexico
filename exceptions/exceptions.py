class EstadoNoExistente(Exception):
    def __init__(self):
        self.message = "El estado no pertenece al conjunto de estados del automata!"
        super().__init__(self.message)

class SimboloNoExistente(Exception):
    def __init__(self):
        self.message = "El caracter no pertenece al alfabeto del automata!"
        super().__init__(self.message)

class ArchivoVacio(Exception):
    def __init__(self):
        self.message = "el archivo esta vacio!"
        super().__init__(self.message)

class EstadoSiguienteNoExiste(Exception):
    def __init__(self):
        self.message = "Simbolo no tiene estado siguiente. Token incorrecto"
        super().__init__(self.message)