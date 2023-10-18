from exceptions import exceptions
from automata_reader import table_reader as tr
from typing import Union, Tuple, Set
from dfa import token
import re
import string

class Dfa:

    def __init__(self):
        pass
        self.__palabras_reservadas : list[str] = ["begin", "end", "do", "if", "for", "cmp", "and", "je", "jmp", "mov"]


    def get_posicion_actual(self) -> tuple[int, int]:
        return (self.__fila, self.__columna)

    def siguiente_estado(self, estado_actual: str, simbolo: str) -> str:
        if not estado_actual in self.estados:
            raise exceptions.EstadoNoExistente

        if not simbolo in self.alfabeto:
            raise exceptions.SimboloNoExistente

        """{ q1 : {1 : q2, 2 : q2} }"""

        siguiente_estado : str = self.transiciones.get(estado_actual).get(simbolo) if not re.fullmatch(r"[0-9A-Za-z]", simbolo) else ""

        if re.fullmatch(r'[0-9A-Za-z]', simbolo):
            for key in self.transiciones.get(estado_actual):
                if simbolo in key:
                    siguiente_estado = self.transiciones.get(estado_actual).get(key)

        if re.fullmatch(f"[{re.escape(string.whitespace)}]", simbolo):
            for key in self.transiciones.get(estado_actual):
                if simbolo in key:
                    siguiente_estado = self.transiciones.get(estado_actual).get(key)

        return siguiente_estado

    def acepta_cadena(self, string : str) -> bool:
        estado : str = self.estado_inicial
        res : bool = False
        
        for pos, let in enumerate(string):
            estado = self.siguiente_estado(estado_actual=estado, simbolo=let)
            
            if pos == len(string)-1 and estado not in self.estados_finales:
                res =  False
                break
            if estado == "":
                res = False
                break
            if pos == len(string)-1 and estado == "":
                res = False
                break
            if pos == len(string)-1 and estado in self.estados_finales:
                res = True
                break
                
        return res
        
    def cargar_datos(self, tabla : tr.table_reader):
        
        self.estados : Set[str] = tabla.estados
        self.alfabeto : Set[str] = tabla.alfabeto
        self.estado_inicial : str = tabla.estado_inicial
        self.estados_finales : Set[str] = tabla.estados_finales
        self.transiciones : dict[str, dict[str, str]] = tabla.transiciones
        self.tokens : dict[str, str] = tabla.tokens
        self.retrocesos : dict[str, int] = tabla.retrocesos
        
        self.__fila : int = 0
        self.__columna : int = 0
        self.__posicion : int = 0
    
    def reiniciar(self):
        self.__posicion = 0
        self.__fila = 0
        self.__columna = 0

    def cargar_archivo_fuente(self, path : str):
        self.__archivo_fuente : str = path

    def get_token(self):
        buffer : str = ""
        with open(self.__archivo_fuente, "r") as file:
            estado : str = self.estado_inicial
            file.seek(self.__posicion)
            
            while char:= file.read(1):
                self.__columna += 1
                self.__posicion = file.tell()   

                if buffer == "" and char in string.whitespace:
                    if char == "\n":
                        self.__columna = 0
                        self.__fila += 1
                    continue

                buffer += char
                    
                estado = self.siguiente_estado(estado_actual=estado, simbolo=char)

                #print(f"char:{char}, buffer:{buffer}, estado:{estado}, posicion:{self.__posicion}, columna:{self.__columna}")

                if not estado:
                    raise exceptions.EstadoSiguienteNoExiste

                if estado in self.estados_finales:
                    temp : list[int] = [self.__fila, self.__columna]
                    if char == "\n":
                        self.__columna = 0
                        self.__fila += 1

                    if self.retrocesos.get(estado) >= 1:
                        buffer = buffer[: -self.retrocesos.get(estado)]
                    
                    self.__posicion -= self.retrocesos.get(estado)
                    self.__columna -= self.retrocesos.get(estado)

                    if buffer in self.__palabras_reservadas:
                        tokencito = token.Token(
                            type="PAL_RES",
                            lexem=buffer,
                            coordinates=(temp[0], temp[1]-1)
                        )
                        return tokencito

                    tokencito = token.Token(type=self.tokens.get(estado),
                                            coordinates=(temp[0], temp[1]-1),
                                            lexem=buffer)

                    return tokencito    
                
                #if estado in self.estados_finales and char in string.whitespace:
                #    temp : list[int] = [self.__fila, self.__columna]
                #    if char == "\n":
                #        self.__columna = 0
                #        self.__fila += 1
#
                #    return token.Token(type=self.tokens.get(estado), coordinates=(temp[0], temp[1]-1), lexem=buffer[:- self.retrocesos.get(estado)])    
                
        return ""