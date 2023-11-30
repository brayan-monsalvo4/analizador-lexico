from exceptions import exceptions
from automata_reader import table_reader as tr
from typing import Union, Tuple, Set
from dfa import token
import re
import string

class Dfa:

    def __init__(self):
        self._total_caracteres : int = 0
        self.posicion : int = 0
        self.reiniciar()
        pass

    def get_posicion_actual(self) -> tuple[int, int]:
        return (self.fila, self.columna)

    def siguiente_estado(self, estado_actual: str, simbolo: str) -> str:
        #print(f"siguiente estado: estado_actual:{estado_actual}, simbolo:{simbolo}")
        if not estado_actual in self.estados:
            raise exceptions.EstadoNoExistente

        siguiente_estado : str = None

        """tratara de obtener el siguiente estado con el simbolo actual, pero si es una expresion regular """
        try:
            siguiente_estado = self.transiciones.get(estado_actual).get(simbolo)
            
            if not siguiente_estado:
                raise Exception
            
        except Exception:
            try:

                for expresion in self.transiciones.get(estado_actual).keys():
                    regex = re.compile(expresion)
                    if regex.fullmatch(simbolo):
                        siguiente_estado = self.transiciones.get(estado_actual).get(expresion)
                        break
                    else:
                        siguiente_estado = None

            except Exception:
                siguiente_estado = None
        

        return siguiente_estado
    
    def acepta_cadena(self, string : str) -> bool:
        estado : str = self.estado_inicial
        res : bool = False
        
        for pos, let in enumerate(string):
            estado = self.siguiente_estado(estado_actual=estado, simbolo=let)
            
            if pos == len(string)-1 and estado not in self.estados_finales:
                res =  False
                break
            if not estado:
                res = False
                break
            if pos == len(string)-1 and not estado:
                res = False
                break
            if pos == len(string)-1 and estado in self.estados_finales:
                res = True
                break
        return res
        
    def cargar_datos(self, tabla : tr.table_reader):
        
        self.estados : Set[str] = tabla.estados
        self.estado_inicial : str = tabla.estado_inicial
        self.estados_finales : Set[str] = tabla.estados_finales
        self.transiciones : dict[str, dict[str, str]] = tabla.transiciones
        self.tokens : dict[str, str] = tabla.tokens
        self.retrocesos : dict[str, int] = tabla.retrocesos
        self.__palabras_reservadas : set[str] = tabla.palabras_reservadas

        self.fila : int = 1
        self.columna : int = 0
        self.posicion : int = 0
    
    def reiniciar(self):
        self.posicion = 0
        self.fila = 1
        self.columna = 1

    def cargar_archivo_fuente(self, path : str):
        self.__archivo_fuente : str = path
        
        with open(self.__archivo_fuente, "r") as file:
            texto = file.read()
            self._total_caracteres = len(texto)

        if not texto or texto[-1] != "\n":
            with open(self.__archivo_fuente, "a") as file:
                file.write("\n")
                self._total_caracteres += 1

        self.reiniciar()

    def get_token(self):
        buffer : str = ""
        with open(self.__archivo_fuente, "r") as file:
            estado : str = self.estado_inicial
            file.seek(self.posicion)

            fin_archivo : bool = False

            while char := file.read(1):
                self.posicion = file.tell()
                self.columna += 1

                buffer += char
                estado = self.siguiente_estado(estado_actual=estado, simbolo=char)

                if self._total_caracteres == self.posicion:
                    fin_archivo = True
                
                if not estado:
                    raise exceptions.LexicoTokenIncorrecto((str(self.fila), str(self.columna)), actual=buffer)
                
                if estado in self.estados_finales:
                    buffer = buffer[: -(self.retrocesos.get(estado)) ] if self.retrocesos.get(estado) else buffer

                    self.posicion -= self.retrocesos.get(estado, 0)# if not fin_archivo else 0
                    self.columna -= self.retrocesos.get(estado, 0)# if not fin_archivo else 0

                    if buffer in self.__palabras_reservadas:
                        tokencito = token.Token(
                            type=buffer,
                            lexem=buffer,
                            coordinates=(self.fila, self.columna)
                        )

                        return tokencito
                    
                    tokencito = token.Token(
                        type=self.tokens.get(estado),
                        lexem=buffer,
                        coordinates=(self.fila, self.columna)
                    )

                    if tokencito.lexem == "\n":
                        self.columna = 1
                        self.fila += 1

                    return tokencito

        return None