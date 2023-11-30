from dfa.token import Token
from dfa.dfa import Dfa
import exceptions.exceptions as exc
from enum import Enum
import copy
from . import estructura

class analizador:
    def __init__(self, analex : Dfa):
        self.token_actual : Token = None
        self.lexic : Dfa = analex
        self.tabla_simbolos : dict = dict()
        self.nombre_programa : str = None
        self.estructura : dict = dict()
        self.datos_estructura : estructura.Structure = estructura.Structure()
        self.nombre_estructura : str = None

    def existe_en_tabla_simbolos(self, identificador : str):
        return identificador in self.tabla_simbolos.keys()
    
    def obtener_valor_apuntado(self, identificador_puntero_token : Token) -> str:
        if not self.existe_en_tabla_simbolos(identificador=identificador_puntero_token.lexem):
            raise exc.SemanticoSimboloNoDeclarado(token=identificador_puntero_token)
        
        if not self.tabla_simbolos[identificador_puntero_token.lexem]["TIPO"] == "POINTER":
            raise exc.SemanticoTokenIncorrecto(token_actual=identificador_puntero_token, tokens=["POINTER"])
        
        valor = self.tabla_simbolos[identificador_puntero_token.lexem]["VALOR"]

        if not valor:
            return None

        return self.tabla_simbolos[valor]

    def son_mismo_tipo(self, lista_tokens: list[Token]):
        print(f"son lo mismo {lista_tokens}")
        return all(token.lexem == lista_tokens[0].lexem for token in lista_tokens)

    def guardar_constante(self, identificador_token : Token, tipo : str, valor : str):
        if self.existe_en_tabla_simbolos(identificador = identificador_token.lexem):
            raise exc.SemanticoSimboloYaExistente(token=identificador_token)
        
        self.tabla_simbolos.update({ identificador_token.lexem : {
            "TIPO" : tipo, 
            "SIMBOLO" : "CONST",
            "VALOR" : valor
        } })

    def guardar_estructura(self, identificador_token : Token, tipo_1 : str, campo_1 : str, tipo_2 : str, campo_2 : str):
        if self.existe_en_tabla_simbolos(identificador=identificador_token.lexem):
            raise exc.SemanticoSimboloYaExistente(token=identificador_token)
        
        if not (tipo_1 == "POINTER" and tipo_2 != "POINTER") and not (tipo_1 != "POINTER" and tipo_2 == "POINTER"):
            raise exc.SemanticoEstructuraIncorrecta(identificador_token)
        
        if not campo_1 != campo_2:
            raise exc.SemanticoEstructuraCamposIguales(token=identificador_token)
        
        tipo_campo, nombre_campo, tipo_apuntador, nombre_apuntador = (tipo_1, campo_1, tipo_2, campo_2) if tipo_1 != "POINTER" else (tipo_2, campo_2, tipo_1, campo_1)

        self.nombre_estructura = identificador_token.lexem

        self.tabla_simbolos.update(
            {
                identificador_token.lexem : {
                    "TIPO" : "ESTRUCTURA",
                    "SIMBOLO" : "ESTRUCTURA",
                    "VALOR" : {
                        "CAMPO" : {
                            "TIPO" : tipo_campo,
                            "NOMBRE" : nombre_campo,
                            "VALOR" : "NULL"
                        },
                        "APUNTADOR" : {
                            "TIPO" : tipo_apuntador,
                            "NOMBRE" : nombre_apuntador,
                            "VALOR" : "NULL"
                        }
                    }
                }
            }
        )

        self.datos_estructura.nombre_estructura = identificador_token.lexem 
        self.datos_estructura.nombre_campo = nombre_campo
        self.datos_estructura.nombre_apuntador = nombre_apuntador
        self.datos_estructura.tipo_campo = tipo_campo
        self.datos_estructura.tipo_apuntador = "POINTER"

    def guardar_variable(self, identificador_token : Token, tipo : str):
        if self.existe_en_tabla_simbolos(identificador=identificador_token.lexem):
            raise exc.SemanticoSimboloYaExistente(token=identificador_token)
        
        if tipo == self.nombre_estructura:
            self.tabla_simbolos.update({
                f"{identificador_token.lexem}.{self.datos_estructura.nombre_campo}" : {
                    "TIPO" : self.datos_estructura.tipo_campo,
                    "SIMBOLO" : self.nombre_estructura,
                    "VALOR" : "NULL"
                }
            })

            self.tabla_simbolos.update({
                f"{identificador_token.lexem}.{self.datos_estructura.nombre_apuntador}" : {
                    "TIPO" : self.datos_estructura.tipo_apuntador,
                    "SIMBOLO" : self.nombre_estructura,
                    "VALOR" : "NULL"
                }
            })

            self.tabla_simbolos.update({
                identificador_token.lexem : {
                    "TIPO" : "ESTRUCTURA",
                    "SIMBOLO" : self.nombre_estructura,
                    "VALOR" : "NULL"
                }
            })

        else:
            self.tabla_simbolos.update({
                identificador_token.lexem : {
                    "TIPO" : tipo,
                    "SIMBOLO" : (simb := "VARS" if not tipo == "POINTER" else "POINTER"),
                    "VALOR" : "NULL"
                }
            })

    def get_next_token(self):
        try:
            self.token_actual = self.lexic.get_token()
            
            while self.token_actual.type == "SEPARADOR": 
                self.token_actual = self.lexic.get_token()

        except AttributeError:
            raise exc.LexicoNoTokenSiguiente

    def match(self, tkns : list[str]):
        #print(f"haciendo match de {self.token_actual.type} en {tkns}")
        if not self.token_actual.type in tkns:
            raise exc.SemanticoTokenFaltante(token_actual=self.token_actual, tokens=tkns)
        
    def predict(self, tkns : list[str]) -> bool:
        return self.token_actual.type in tkns

    def S (self):
        self.get_next_token()
        self.match(["PROGRAM"])

        self.get_next_token()
        self.match(["IDENTIFICADOR"])

        self.nombre_programa = self.token_actual.lexem
        self.tabla_simbolos.update({self.nombre_programa : "NOMBRE_PROGRAMA"})
        self.get_next_token()
        self.A()

    def A(self):
        self.match(["BEGIN", "CONST", "STRUCTURE", "VARS"])

        self.B()

        self.C()
        
        self.D()
        
        self.match(["BEGIN"])

        self.get_next_token()
        self.E()

        self.match(["END"])     

        try:
            self.get_next_token()
        except exc.LexicoNoTokenSiguiente:
            if self.token_actual == None:
                print("programa aceptado xd")
            else: 
                raise exc.SemanticoProgramaIncorrecto(token=self.token_actual)
            
    def B(self):
        if self.predict(["CONST"]):
            self.get_next_token()
            self.BP()
        elif self.predict(["BEGIN", "STRUCTURE", "VARS"]):
            return
        else:
            raise Exception

    def BP(self):
        if self.predict(["IDENTIFICADOR"]):
            nombre_constante = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["ASIGNA"]) 
            
            self.get_next_token()
            tipo = self.VALOR()
            valor = self.token_actual.lexem

            self.guardar_constante(identificador_token=nombre_constante, tipo=tipo, valor=valor)

            self.get_next_token()
            self.BP()

        elif self.predict(["BEGIN", "STRUCTURE", "VARS"]):
            return
        
        else:
            raise Exception
        
    def C(self):
        if self.predict(["STRUCTURE"]):
            self.get_next_token()
            self.CC()
            
            #self.get_next_token()
        if self.predict(["BEGIN", "VARS"]):
            return

    def CC(self):
        if self.predict(["IDENTIFICADOR"]):
            nombre_estructura = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["ASIGNA"])

            self.get_next_token()
            self.match(["LLAV_A"])

            self.get_next_token()
            tipo_1 = self.TIPO()

            self.get_next_token()
            self.match("IDENTIFICADOR")

            campo_1 = self.token_actual.lexem

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            self.get_next_token()
            tipo_2 = self.TIPO()

            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            campo_2 = self.token_actual.lexem

            self.get_next_token()
            self.match(["PUNTO_COMA"])
            #self.nombre_estructura = nombre_estructura.lexem
            self.guardar_estructura(identificador_token=nombre_estructura, tipo_1=tipo_1, campo_1=campo_1, tipo_2=tipo_2, campo_2=campo_2)

            self.get_next_token()
            self.match(["LLAV_C"])
            #print(f"estructura: {nombre_estructura.lexem} = {tipo_1} {campo_1} ; {tipo_2} {campo_2}")
            self.get_next_token()
        elif self.predict(["BEGIN", "VARS"]):
            return
        else:
            raise Exception
        
    def D(self):
        if self.predict(["VARS"]):
            self.get_next_token()
            self.DP()

        elif self.predict(["BEGIN"]):
            return

    def DP(self):
        print(self.nombre_estructura)
        if self.predict(["INT", "CHAR", "STRING", "POINTER"]):
            tipo = self.token_actual.type
            
            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            self.guardar_variable(identificador_token=self.token_actual, tipo=tipo)            

            self.get_next_token()
            self.DPP(tipo = tipo)
            
            self.match("PUNTO_COMA") 

            self.get_next_token()
            self.DP()  

        elif self.predict(["IDENTIFICADOR"]) and self.token_actual.lexem == self.nombre_estructura:
            print("entro estructura")
            tipo = self.nombre_estructura
            print(f"tipo en estructura : {tipo}")

            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            identificador = copy.deepcopy(self.token_actual)
            print(f"identificador en estructura {identificador}")

            self.guardar_variable(identificador_token=identificador, tipo=tipo)

            self.get_next_token()
            self.DPP(tipo = tipo)

            self.match(["PUNTO_COMA"])

            self.get_next_token()
            self.DP()
            
        
        elif self.predict(["BEGIN"]):
            return
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["INT", "CHAR", "STRING", "POINTER", "BEGIN"])
        
    def DPP(self, tipo):

        if self.predict(["COMA"]):
            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            self.guardar_variable(identificador_token=self.token_actual, tipo=tipo)

            self.get_next_token()
            self.DPP(tipo=tipo)

        elif self.predict(["PUNTO_COMA"]):
            return
        else:
            raise Exception

    def E(self, perform : bool = True):
        if self.predict(["IDENTIFICADOR"]):
            primer_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["ASIGNA"])

            self.get_next_token()
            self.E_I(perform=perform, primer_token=primer_token)

        elif self.predict(["ESTRUCTURA"]):
            primer_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["ASIGNA"])

            self.get_next_token()
            self.E_I(perform=perform, primer_token=primer_token)

        elif self.predict(["READ"]):
            self.get_next_token()
            self.READ()

        elif self.predict(["WRITE"]):
            self.get_next_token()
            self.WRITE()
        
        elif self.predict(["WHILE"]):
            self.match(["WHILE"])
            self.get_next_token()
            self.WHILE()

        elif self.predict(["IF"]):
            self.match(["IF"])
            self.get_next_token()
            self.IF()

        elif self.predict(["END", "ELSE"]):
            return 
        else:
            raise exc.SemanticoTokenIncorrecto(tokens=["IDENTIFICADOR", "ESTRUCTURA", "END","ELSE"], token_actual=self.token_actual)

    def E_I(self, perform : bool, primer_token : Token):
        if self.predict(["INT", "CHAR", "STRING", "NULL"]):
            segundo_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_II(perform=perform, primer_token=primer_token, segundo_token=segundo_token)

        elif self.predict(["IDENTIFICADOR"]):
            segundo_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_II(perform=perform, primer_token=primer_token, segundo_token=segundo_token)

        elif self.predict(["ESTRUCTURA"]):
            segundo_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_II(perform=perform, primer_token=primer_token, segundo_token=segundo_token)

        else:
            raise exc.SemanticoTokenIncorrecto(tokens=["INT", "CHAR", "STRING", "NULL", "IDENTIFICADOR", "ESTRUCTURA"], token_actual=self.token_actual)
        
    def validar_casos(self, token_izquierdo : Token, token_derecho : Token):
        if not self.existe_en_tabla_simbolos(identificador=token_derecho.lexem):

            if not token_derecho.type in ["INT", "CHAR", "STRING", "NULL"]:
                raise exc.SemanticoSimboloNoDeclarado(token=token_derecho)
            
            elif token_derecho.type == "NULL" and token_derecho.lexem == "NULL":
                self.tabla_simbolos[token_izquierdo.lexem]["VALOR"] = "NULL"

            elif self.tabla_simbolos[token_izquierdo.lexem]["TIPO"] != token_derecho.type:
                raise exc.SemanticoTokensIncompatibles(tokens=[token_izquierdo, token_derecho])

            else:
                self.tabla_simbolos[token_izquierdo.lexem]["VALOR"] = token_derecho.lexem

        #variables
        elif self.tabla_simbolos[token_derecho.lexem]["SIMBOLO"] == "VARS":
            if not self.tabla_simbolos[token_izquierdo.lexem]["TIPO"] == self.tabla_simbolos[token_derecho.lexem]["TIPO"]:
                raise exc.SemanticoTokensIncompatibles(tokens=[token_derecho, token_izquierdo])
            
            self.tabla_simbolos[token_izquierdo.lexem]["VALOR"] = self.tabla_simbolos[token_derecho.lexem]["VALOR"]

        #constantes
        elif self.tabla_simbolos[token_derecho.lexem]["SIMBOLO"] == "CONST":
            if not self.tabla_simbolos[token_izquierdo.lexem]["TIPO"] == self.tabla_simbolos[token_derecho.lexem]["TIPO"]:
                raise exc.SemanticoTokensIncompatibles(tokens=[token_derecho, token_izquierdo])
            
            self.tabla_simbolos[token_izquierdo.lexem]["VALOR"] = self.tabla_simbolos[token_derecho.lexem]["VALOR"]

        #estructura con campo
        elif self.tabla_simbolos[token_derecho.lexem]["SIMBOLO"] == self.datos_estructura.nombre_estructura:
            if not self.tabla_simbolos[token_izquierdo.lexem]["TIPO"] == self.tabla_simbolos[token_derecho.lexem]["TIPO"]:
                raise exc.SemanticoTokensIncompatibles(tokens=[token_derecho, token_izquierdo])
            
            self.tabla_simbolos[token_izquierdo.lexem]["VALOR"] = self.tabla_simbolos[token_derecho.lexem]["VALOR"]

    def validar_caso_puntero(self, token_izquierdo : Token, token_derecho : Token):
        if not self.existe_en_tabla_simbolos(identificador=token_derecho.lexem):
            print("entro caoso pntero xd")

            if token_derecho.type in ["INT", "CHAR", "STRING"]:
                raise exc.SemanticoTokensIncompatibles(tokens=[token_izquierdo, token_derecho])
            
            elif token_derecho.type == "NULL" and token_derecho.lexem == "NULL":
                print(f" panchito : {token_derecho.lexem}")
                self.tabla_simbolos[token_izquierdo.lexem]["VALOR"] = "NULL"

        if not self.existe_en_tabla_simbolos(identificador=token_derecho.lexem):
                raise exc.SemanticoSimboloNoDeclarado(token=token_derecho)
        
        self.tabla_simbolos[token_izquierdo.lexem]["VALOR"] = token_derecho.lexem

    def validar_caso_estructura(self, token_izquierdo : Token, token_derecho : Token):
        if not self.existe_en_tabla_simbolos(identificador=token_izquierdo.lexem):
            raise exc.SemanticoSimboloNoDeclarado(token=token_izquierdo)
        elif not self.existe_en_tabla_simbolos(identificador=token_derecho.lexem):
        
            raise exc.SemanticoSimboloNoDeclarado(token=token_derecho)
        
        self.tabla_simbolos[f"{token_izquierdo.lexem}.{self.datos_estructura.nombre_campo}"]["VALOR"] = self.tabla_simbolos[f"{token_derecho.lexem}.{self.datos_estructura.nombre_campo}"]["VALOR"]
        self.tabla_simbolos[f"{token_izquierdo.lexem}.{self.datos_estructura.nombre_apuntador}"]["VALOR"] = self.tabla_simbolos[f"{token_derecho.lexem}.{self.datos_estructura.nombre_apuntador}"]["VALOR"]
        
    def E_II(self, perform : bool, primer_token : Token, segundo_token : Token):
        if self.predict(["SUMA", "RESTA", "DIV", "MULTI"]):
            tercer_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_III(perform=perform, primer_token=primer_token, segundo_token=segundo_token, tercer_token=tercer_token)
        
        elif self.predict(["PUNTO_COMA"]):


            if not self.existe_en_tabla_simbolos(identificador=primer_token.lexem):
                raise exc.SemanticoSimboloNoDeclarado(token=primer_token)
            elif self.tabla_simbolos[primer_token.lexem]["TIPO"] == "ESTRUCTURA" and self.tabla_simbolos[segundo_token.lexem]["TIPO"] == "ESTRUCTURA":
                self.validar_caso_estructura(token_izquierdo=primer_token, token_derecho=segundo_token)
            elif self.tabla_simbolos[primer_token.lexem]["TIPO"] == "POINTER":
                self.validar_caso_puntero(token_izquierdo=primer_token, token_derecho=segundo_token)
            elif self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "VARS" or self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == self.datos_estructura.nombre_estructura:
                self.validar_casos(token_izquierdo=primer_token, token_derecho=segundo_token)
            elif self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "CONST":
                raise exc.SemanticoSobreescribirConstante(constante=primer_token)

            self.get_next_token()
            self.E(perform=perform)

            return 
        
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["SUMA", "RESTA", "DIV", "MULTI", "PUNTO_COMA"])

    def E_III(self, perform : bool, primer_token : Token, segundo_token : Token, tercer_token : Token):
        if self.predict(["INT", "CHAR", "STRING", "NULL"]):
            cuarto_token = self.token_actual

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            if not self.existe_en_tabla_simbolos(identificador=primer_token.lexem):
                raise exc.SemanticoSimboloNoDeclarado(token=primer_token)
            
            if not self.existe_en_tabla_simbolos(identificador=segundo_token.lexem):
                if not segundo_token.type in ["INT", "CHAR", "STRING", "NULL"]:
                    raise exc.SemanticoSimboloNoDeclarado(token=segundo_token)
                primer_operando = None if segundo_token.lexem == "NULL" else segundo_token.lexem
            else:
                primer_operando = None if self.tabla_simbolos[segundo_token.lexem]["VALOR"] == "NULL" else self.tabla_simbolos[segundo_token.lexem]["VALOR"]
            

            operacion = tercer_token.lexem
            segundo_operando = None if cuarto_token.lexem == "NULL" else cuarto_token.lexem
            
            if perform:
                try:
                    print(f"{primer_operando}{operacion}{segundo_operando}")
                    resultado = eval(f"{primer_operando}{operacion}{segundo_operando}")
                    print(f"{resultado}  {type(resultado)}")

                    if type(resultado) == int and self.tabla_simbolos[primer_token.lexem]["TIPO"] == "INT":
                        self.tabla_simbolos[primer_token.lexem]["VALOR"] = str(resultado)
                    elif type(resultado) == str and self.tabla_simbolos[primer_token.lexem]["TIPO"] == "STRING":
                        self.tabla_simbolos[primer_token.lexem]["VALOR"] = str(resultado)
                    elif type(resultado) == int and self.tabla_simbolos[primer_token.lexem]["TIPO"] != "INT":
                        raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])
                    elif type(resultado) == str and self.tabla_simbolos[primer_operando]["TIPO"] != "STRING":
                        raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])

                except Exception as e:
                    raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])

            self.get_next_token()
            self.E(perform=perform)
        
        elif self.predict(["IDENTIFICADOR"]):
            cuarto_token = self.token_actual

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            if not self.existe_en_tabla_simbolos(identificador=primer_token.lexem):
                raise exc.SemanticoSimboloNoDeclarado(token=primer_token)
            
            if not self.existe_en_tabla_simbolos(identificador=segundo_token.lexem):
                if not segundo_token.type in ["INT", "CHAR", "STRING", "NULL"]:
                    raise exc.SemanticoSimboloNoDeclarado(token=segundo_token)
                
                primer_operando = None if segundo_token.lexem == "NULL" else segundo_token.lexem
            else:
                primer_operando = None if self.tabla_simbolos[segundo_token.lexem]["VALOR"] == "NULL" else self.tabla_simbolos[segundo_token.lexem]["VALOR"]
            
            if not self.existe_en_tabla_simbolos(identificador=cuarto_token.lexem):
                raise exc.SemanticoSimboloNoDeclarado(token=cuarto_token)
            else:
                segundo_operando = None if self.tabla_simbolos[cuarto_token.lexem]["VALOR"] == "NULL" else self.tabla_simbolos[cuarto_token.lexem]["VALOR"]

            operacion = tercer_token.lexem

            if perform:
                try:
                    print(f"{primer_operando}{operacion}{segundo_operando}")
                    resultado = eval(f"{primer_operando}{operacion}{segundo_operando}")
                    print(f"{resultado}  {type(resultado)}")

                    if type(resultado) == int and self.tabla_simbolos[primer_token.lexem]["TIPO"] == "INT":
                        self.tabla_simbolos[primer_token.lexem]["VALOR"] = str(resultado)
                    elif type(resultado) == str and self.tabla_simbolos[primer_token.lexem]["TIPO"] == "STRING":
                        self.tabla_simbolos[primer_token.lexem]["VALOR"] = str(resultado)
                    elif type(resultado) == int and self.tabla_simbolos[primer_token.lexem]["TIPO"] != "INT":
                        raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])
                    elif type(resultado) == str and self.tabla_simbolos[primer_operando]["TIPO"] != "STRING":
                        raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])

                except Exception as e:
                    raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])

            self.get_next_token()
            self.E(perform=perform)

        elif self.predict(["ESTRUCTURA"]):
            cuarto_token = self.token_actual
            
            self.get_next_token()
            self.match(["PUNTO_COMA"])

            if not self.existe_en_tabla_simbolos(identificador=primer_token.lexem):
                raise exc.SemanticoSimboloNoDeclarado(token=primer_token)
            
            if not self.existe_en_tabla_simbolos(identificador=segundo_token.lexem):
                if not segundo_token.type in ["INT", "CHAR", "STRING", "NULL"]:
                    raise exc.SemanticoSimboloNoDeclarado(token=segundo_token)
                
                primer_operando = None if segundo_token.lexem == "NULL" else segundo_token.lexem
            else:
                primer_operando = None if self.tabla_simbolos[segundo_token.lexem]["VALOR"] == "NULL" else self.tabla_simbolos[segundo_token.lexem]["VALOR"]
            
            if not self.existe_en_tabla_simbolos(identificador=cuarto_token.lexem):
                raise exc.SemanticoSimboloNoDeclarado(token=cuarto_token)
            else:
                segundo_operando = None if self.tabla_simbolos[cuarto_token.lexem]["VALOR"] == "NULL" else self.tabla_simbolos[cuarto_token.lexem]["VALOR"]

            operacion = tercer_token.lexem

            if perform:
                try:
                    print(f"{primer_operando}{operacion}{segundo_operando}")
                    resultado = eval(f"{primer_operando}{operacion}{segundo_operando}")
                    print(f"{resultado}  {type(resultado)}")

                    if type(resultado) == int and self.tabla_simbolos[primer_token.lexem]["TIPO"] == "INT":
                        self.tabla_simbolos[primer_token.lexem]["VALOR"] = str(resultado)
                    elif type(resultado) == str and self.tabla_simbolos[primer_token.lexem]["TIPO"] == "STRING":
                        self.tabla_simbolos[primer_token.lexem]["VALOR"] = str(resultado)
                    elif type(resultado) == int and self.tabla_simbolos[primer_token.lexem]["TIPO"] != "INT":
                        raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])
                    elif type(resultado) == str and self.tabla_simbolos[primer_operando]["TIPO"] != "STRING":
                        raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])

                except Exception as e:
                    raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token, cuarto_token])

            self.get_next_token()
            self.E(perform=perform)
        
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["INT", "CHAR", "STRING", "NULL", "IDENTIFICADOR", "ESTRUCTURA"])

    def READ(self):
        self.match(["PAR_A"])

        self.get_next_token()
        self.match(["IDENTIFICADOR"])

        variable_donde_guardar = self.token_actual.lexem

        self.get_next_token()
        self.match(["PAR_C"])

        self.get_next_token()
        self.match(["PUNTO_COMA"])

        print(f"READ : ({variable_donde_guardar})")

        self.get_next_token()
        self.E()

    def WRITE(self):
        self.match(["PAR_A"])

        self.get_next_token()
        tipo = self.M()
        dato = None

        if tipo == "IDENTIFICADOR":
            if not self.existe_en_tabla_simbolos(identificador=self.token_actual.lexem):
                raise exc.SemanticoSimboloNoDeclarado(token=self.token_actual)

            dato = self.tabla_simbolos[self.token_actual.lexem]["VALOR"] if self.token_actual.lexem != self.struct.nombre_estructura else self.estructura
        else:
            dato = self.token_actual.lexem
        
        
        self.get_next_token()
        self.match(["PAR_C"])

        self.get_next_token()
        self.match(["PUNTO_COMA"])

        print(f"write : ({tipo} {dato})")

        self.get_next_token()
        self.E()

    def IF(self):
        self.match(["PAR_A"])

        self.get_next_token()
        res = self.CON()
        print(res)

        self.get_next_token()
        self.match(["PAR_C"])

        self.get_next_token()
        self.match(["THEN"])

        self.get_next_token()
        self.E(perform=res)

        self.IF_P()

        self.match(["END"])

        self.get_next_token()
        self.E()

    def IF_P(self):
        if self.predict(["ELSE"]):
            self.get_next_token()
            self.E()
        
        elif self.predict(["END"]):
            return 
    
    def WHILE(self):
        self.match(["PAR_A"])

        self.get_next_token()
        res = self.CON()
        print(res)

        self.get_next_token()
        self.match(["PAR_C"])

        self.get_next_token()
        self.match(["DO"])

        self.get_next_token()
        self.E()

        self.match(["END"])

        self.get_next_token()
        self.E()
    
    def CON(self) -> bool:
        if self.predict(["INT", "CHAR", "STRING", "NULL", "IDENTIFICADOR"]):
            tipo_operando_1 = self.M()
            if tipo_operando_1 == "IDENTIFICADOR" and (not self.existe_en_tabla_simbolos(identificador=self.token_actual.lexem)):
                raise Exception
            valor_operando_1 = self.tabla_simbolos[self.token_actual.lexem]["VALOR"] if tipo_operando_1 == "IDENTIFICADOR" else self.token_actual.lexem

            self.get_next_token()
            operacion = self.OPCO()

            self.get_next_token()
            tipo_operando_2 = self.M()
            if tipo_operando_2 == "IDENTIFICADOR" and (not self.existe_en_tabla_simbolos(identificador=self.token_actual.lexem)):
                raise Exception
            valor_operando_2 = self.tabla_simbolos[self.token_actual.lexem]["VALOR"] if tipo_operando_2 == "IDENTIFICADOR" else self.token_actual.lexem
            
            try:
                if operacion == "MENOR":
                    valor_operando_1 = int(valor_operando_1)
                    valor_operando_2 = int(valor_operando_2)

                    return valor_operando_1 < valor_operando_2

                elif operacion == "MAYOR":
                    valor_operando_1 = int(valor_operando_1)
                    valor_operando_2 = int(valor_operando_2)

                    return valor_operando_1 > valor_operando_2

                elif operacion == "MENOR_IGUAL":
                    valor_operando_1 = int(valor_operando_1)
                    valor_operando_2 = int(valor_operando_2)

                    return valor_operando_1 <= valor_operando_2

                elif operacion == "MAYOR_IGUAL":
                    valor_operando_1 = int(valor_operando_1)
                    valor_operando_2 = int(valor_operando_2)

                    return valor_operando_1 > valor_operando_2

                elif operacion == "IDENTICO":
                    return valor_operando_1 == valor_operando_2

                elif operacion == "DISTINTO":
                    return valor_operando_1 != valor_operando_2
            except ValueError:
                print(self.token_actual)
                raise Exception

    def VALOR(self) -> str:            
        self.match(["INT", "CHAR", "STRING", "NULL"])

        return self.token_actual.type

    def TIPO(self) -> str:
        self.match(["INT", "CHAR", "STRING", "POINTER"])

        return self.token_actual.type 
        
    def OPCO(self) -> str:
        self.match(["MENOR", "MAYOR", "MENOR_IGUAL", "MAYOR_IGUAL", "IDENTICO", "DISTINTO"])

        return self.token_actual.type
        
    def OPMA(self) -> str:
        self.match(["SUMA", "RESTA", "MULTI", "DIV", "MOD"])

        return self.token_actual.type

    def M(self) -> str:
        if self.predict(["IDENTIFICADOR"]):
            return self.token_actual.type
        elif self.predict(["INT", "CHAR", "STRING", "NULL"]):
            return self.VALOR()
        elif self.predict(["ESTRUCTURA"]):
            return self.token_actual.type
        else:
            raise Exception
    