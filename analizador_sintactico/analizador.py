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
        self.struct : estructura.Structure = estructura.Structure()
    
    def existe_en_tabla_simbolos(self, identificador : str) -> bool:
        return identificador in self.tabla_simbolos.keys() or identificador == self.struct.nombre_estructura
    
    def son_mismo_tipo_hard(self, id_tokens: list[Token]):
        lista_auxiliar : list[str] = list()
        for token in id_tokens:
            lista_auxiliar.append( self.tabla_simbolos[token]["TIPO"] )

        if not all(tipo == lista_auxiliar[0] for tipo in lista_auxiliar):
            raise exc.SemanticoTokensIncompatibles(tokens=id_tokens) 

    def existe_en_tabla_simbolos_hard(self, token : Token):
        if not token.lexem in self.tabla_simbolos.keys() or token.lexem == self.struct.nombre_estructura:
            raise exc.SemanticoSimboloNoDeclarado(token=token)

    def consultar_variable_apuntada(self, id_apuntador : str) -> str:
        return self.tabla_simbolos[id_apuntador]["VALOR"] 

    def guardar_constante(self, identificador : str, tipo : str, valor : str):
        if self.existe_en_tabla_simbolos(identificador=identificador):
            raise Exception

        self.tabla_simbolos.update( { identificador : { "TIPO" : tipo , "VALOR" : valor,  "SIMBOLO" : "CONST"}} )
        #print(f"guardando {self.tabla_simbolos}")

    def guardar_variable(self, identificador : str, tipo : str, valor : str):
        if self.existe_en_tabla_simbolos(identificador=identificador):
            raise Exception
        
        self.tabla_simbolos.update( { identificador : {"TIPO" : tipo , "VALOR" : valor, "SIMBOLO" : "VARS"} } ) if tipo != "POINTER" else self.tabla_simbolos.update( { identificador : {"TIPO" : tipo , "VALOR" : valor, "SIMBOLO" : tipo} } )
        #print(f"guardando {self.tabla_simbolos}")

    def guardar_estructura(self, identificador : str):
        if self.existe_en_tabla_simbolos(identificador=identificador):
            raise Exception
        
        self.tabla_simbolos.update(  { 
                            identificador : { 
                                    "TIPO" : "STRUCT", 
                                    "SIMBOLO" : "STRUCT",
                                    "VALOR" : {
                                        "CAMPO" : {
                                            "NOMBRE" : self.struct.nombre_campo,
                                            "TIPO" : self.struct.tipo_campo,
                                            "VALOR" : "NULL"
                                        },
                                        "APUNTADOR": {
                                            "NOMBRE" : self.struct.nombre_apuntador,
                                            "TIPO" : self.struct.tipo_apuntador,
                                            "VALOR" : "NULL"
                                        }
                                    }
                                    } 
                            }
                        )

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
            id = self.token_actual.lexem

            self.get_next_token()
            self.match(["ASIGNA"]) 
            
            self.get_next_token()
            tipo = self.VALOR()

            self.guardar_constante(identificador=id, tipo=tipo, valor=self.token_actual.lexem)
            
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
            nombre_estructura = self.token_actual.lexem

            if self.existe_en_tabla_simbolos(identificador=nombre_estructura):
                raise Exception

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

            if tipo_1 == "POINTER" and tipo_2 != "POINTER":
                self.estructura.update(  { 
                                            nombre_estructura : { 
                                                    "TIPO" : "STRUCT", 
                                                    "SIMBOLO" : "STRUCT",
                                                    "VALOR" : {
                                                        "CAMPO" : {
                                                            "NOMBRE" : campo_2,
                                                            "TIPO" : tipo_2,
                                                            "VALOR" : "NULL"
                                                        },
                                                        "APUNTADOR": {
                                                            "NOMBRE" : campo_1,
                                                            "TIPO" : tipo_1,
                                                            "VALOR" : "NULL"
                                                        }
                                                    }
                                                    } 
                                            }
                                        )
                self.struct.nombre_estructura = nombre_estructura
                self.struct.nombre_campo = campo_2
                self.struct.tipo_campo = tipo_2
                self.struct.valor_campo = "NULL"
                self.struct.nombre_apuntador = campo_1
                self.struct.tipo_apuntador = tipo_1
                self.struct.valor_apuntador = "NULL"
            elif tipo_1 != "POINTER" and tipo_2 == "POINTER":
                self.estructura.update(  { 
                                            nombre_estructura : { 
                                                    "TIPO" : "STRUCT", 
                                                    "SIMBOLO" : "STRUCT",
                                                    "VALOR" : {
                                                        "CAMPO" : {
                                                            "NOMBRE" : campo_1,
                                                            "TIPO" : tipo_1,
                                                            "VALOR" : "NULL"
                                                        },
                                                        "APUNTADOR": {
                                                            "NOMBRE" : campo_2,
                                                            "TIPO" : tipo_2,
                                                            "VALOR" : "NULL"
                                                        }
                                                    }
                                                    } 
                                            }
                                        )
                self.struct.nombre_estructura = nombre_estructura
                self.struct.nombre_campo = campo_1
                self.struct.tipo_campo = tipo_1
                self.struct.valor_campo = "NULL"
                self.struct.nombre_apuntador = campo_2
                self.struct.tipo_apuntador = tipo_2
                self.struct.valor_apuntador = "NULL"
            else:
                raise Exception
            
            self.get_next_token()
            self.match(["LLAV_C"])
            print(f"estructura: {nombre_estructura} = {tipo_1} {campo_1} ; {tipo_2} {campo_2}")
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
        conjunto_predictivo = ["INT", "CHAR", "STRING", "POINTER"]
        es_estructura = False
        
        if self.token_actual.type == "IDENTIFICADOR":
            if not self.token_actual.lexem == self.struct.nombre_estructura:
                raise Exception
            
            conjunto_predictivo.append("IDENTIFICADOR")
            es_estructura = True

        if self.predict(conjunto_predictivo):
            tipo = self.token_actual.lexem if es_estructura else self.token_actual.type

            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            if es_estructura:
                self.guardar_estructura(identificador=self.token_actual.lexem)
            else:
                self.guardar_variable(identificador=self.token_actual.lexem, tipo=tipo, valor="NULL")

            
            self.get_next_token()
            self.DPP(type=tipo, es_estructura=es_estructura)
            
            self.match("PUNTO_COMA") 

            self.get_next_token()
            self.DP()  
        
        elif self.predict(["BEGIN"]):
            return
        else:
            raise Exception
        
    def DPP(self, type : str, es_estructura : bool):
        if self.predict(["COMA"]):
            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            if es_estructura:
                self.guardar_estructura(identificador=self.token_actual.lexem)
            else:
                self.guardar_variable(identificador=self.token_actual.lexem, tipo=type, valor="NULL")

            self.get_next_token()
            self.DPP(type, es_estructura=es_estructura)
        elif self.predict(["PUNTO_COMA"]):
            return
        else:
            raise Exception

    def E (self, perform : bool = True):
        if self.predict(["IDENTIFICADOR"]):
            primer_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_I(primer_token=primer_token)
        
        elif self.predict(["READ"]):
            self.match(["READ"])
            self.get_next_token()
            self.READ()
        
        elif self.predict(["WRITE"]):
            self.match(["WRITE"])
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
            raise exc.SemanticoTokenIncorrecto(tokens=["IDENTIFICADOR", "READ", "WRITE", "WHILE", "IF", "END", "ELSE"],token_actual=self.token_actual)

    def E_I(self, primer_token : Token):
        if self.predict(["ASIGNA"]):
            self.get_next_token()
            self.E_II(primer_token=primer_token)

        elif self.predict(["PUNTO"]):
            self.get_next_token()
            self.E_III(primer_token=primer_token)
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["=", "."])

    def E_II(self, primer_token : Token):
        if self.predict(["IDENTIFICADOR"]):
            seg_token= copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_IV(primer_token=primer_token, segundo_token =seg_token)

        elif self.predict(["INT", "CHAR", "STRING", "NULL"]):
            seg_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_V(primer_token=primer_token, segundo_token=seg_token)
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["IDENTIFICADOR", "INT", "CHAR", "STRING", "NULL"])

    def E_III(self, primer_token : Token):
        self.match(["IDENTIFICADOR"])

        seg_token = copy.deepcopy(self.token_actual)
        
        self.get_next_token()
        self.E_VI(primer_token=primer_token, segundo_token=seg_token)

    def E_IV(self, primer_token : Token, segundo_token : Token):
        if self.predict(["SUMA", "RESTA", "MULTI", "DIV", "MOD"]):
            tercer_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_VII(primer_token=primer_token, segundo_token=segundo_token, tercer_token=tercer_token)
        
        elif self.predict(["PUNTO_COMA"]):
            """ AQUI SE ENCUENTRA EL FIN DE LA ASIGNACION SIMPLE ID = ID  """
            
            print(f"{primer_token.lexem} = {segundo_token.lexem}")

            self.existe_en_tabla_simbolos_hard(token=primer_token)
            self.existe_en_tabla_simbolos_hard(token=segundo_token)

            """casos:
            constante = variable        #invalido   #LISTO
            constante = constante       #invalido   #LISTO
            constante = estructura      #invalido   #LISTO
            constante = apuntador       #invalido   #LISTO

            variable = constante        #valido cuando sean del mismo tipo      #LISTO
            variable = estructura       #invalido                               #LISTO
            variable = apuntador        #valido cuando el apuntador apunte hacia una variable del mismo tipo        #PENDIENTE DE PROBAR
            variable = variable         #valido cuando sean del mismo tipo      #LISTO
            

            apuntador = apuntador       #valido                                 #LISTO
            apuntador = constante       #valido                                 #LISTO
            apuntador = estructura      #valido                                 #LISTO
            apuntador = variable        #valido                                 #LISTO

            estructura = estructura     #valido                                 #PENDIENTE
            estructura = constante      #invalido                               #LISTO
            estructura = apuntador      #valido cuando el apunte apunte hacia una estructura        #LISTO
            estructura = variable       #invalido                               #LISTO
            """

            if self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "CONST":
                raise exc.SemanticoSobreescribirConstante(constante=primer_token)
        
            elif self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "VARS":
                if self.tabla_simbolos[segundo_token.lexem]["SIMBOLO"] == "CONST":
                    self.son_mismo_tipo_hard(id_tokens=[primer_token.lexem, segundo_token.lexem])
                    self.tabla_simbolos[primer_token.lexem]["VALOR"] = self.tabla_simbolos[segundo_token.lexem]["VALOR"]
                
                elif self.tabla_simbolos[segundo_token.lexem]["SIMBOLO"] == "STRUCT":
                    raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token])

                elif self.tabla_simbolos[segundo_token.lexem]["SIMBOLO"] == "POINTER":
                    variable = self.consultar_variable_apuntada(id_apuntador=segundo_token.lexem)
                    self.son_mismo_tipo_hard(id_tokens=[primer_token.lexem, variable])
                    self.tabla_simbolos[primer_token.lexem]["VALOR"] = self.tabla_simbolos[variable]["VALOR"]
                
                elif self.tabla_simbolos[segundo_token.lexem]["SIMBOLO"] == "VARS":
                    self.son_mismo_tipo_hard(id_tokens=[primer_token.lexem, segundo_token.lexem])
                    self.tabla_simbolos[primer_token.lexem]["VALOR"] = self.tabla_simbolos[segundo_token.lexem]["VALOR"]

            elif self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "POINTER":
                self.tabla_simbolos[primer_token.lexem]["VALOR"] =  segundo_token.lexem

            elif self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "STRUCT":
                if self.tabla_simbolos[segundo_token.lexem]["SIMBOLO"] == "STRUCT":
                    self.son_mismo_tipo_hard(id_tokens=[primer_token.lexem, segundo_token.lexem])
                    self.tabla_simbolos[primer_token.lexem]["VALOR"] = self.tabla_simbolos[segundo_token.lexem]["VALOR"]
                
                if self.tabla_simbolos[segundo_token.lexem]["SIMBOLO"] == "CONST" or self.tabla_simbolos[segundo_token.lexem]["SIMBOLO"] == "VARS":
                    raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token])
                
                if self.tabla_simbolos[segundo_token.lexem]["SIMBOLO"] == "POINTER":
                    variable = self.consultar_variable_apuntada(id_apuntador=segundo_token.lexem)
                    print(f"variable {variable}")

                    self.son_mismo_tipo_hard(id_tokens=[primer_token.lexem, variable])

                    self.tabla_simbolos[primer_token.lexem]["VALOR"] = self.tabla_simbolos[variable]["VALOR"]
                    

            self.get_next_token()
            self.E()
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["SUMA", "RESTA", "MULTI", "DIV", "MOD"])
    
    def E_V(self, primer_token : Token, segundo_token : Token):
        if self.predict(["PUNTO_COMA"]):
            """AQUI SE ENCUENTRA EL FIN DE LA ASIGNACION SIMPLE ID = VALOR"""
            print(f"{primer_token.lexem} = {segundo_token.lexem}")
            print(f"primer tipo {primer_token.type} segundo tipo {segundo_token.type}") 
            tipo = self.tabla_simbolos[primer_token.lexem]["TIPO"]
            print(f"{tipo}")
            
            """
            casos:

            constante = valor           #invalido                                   #LISTO

            variable = valor            #valido cuando sean del mismo tipo          #LISTO

            apuntador = valor           #valido cuando el tipo sea NULL             #LISTO

            estructura = valor          #valido cuando tipo sea NULL                #LISTO
            """

            self.existe_en_tabla_simbolos_hard(token=primer_token)

            if self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "CONST":
                raise exc.SemanticoSobreescribirConstante(constante=primer_token.lexem)
            
            elif self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "VARS":
                if segundo_token.type != "NULL" and self.tabla_simbolos[primer_token.lexem]["TIPO"] != segundo_token.type:
                    raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token])

                self.tabla_simbolos[primer_token.lexem]["VALOR"] = segundo_token.lexem

            elif self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "POINTER":
                if segundo_token.lexem != "NULL":
                    raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token])
                
                self.tabla_simbolos[primer_token.lexem]["VALOR"] = "NULL"
            
            elif self.tabla_simbolos[primer_token.lexem]["SIMBOLO"] == "STRUCT":
                if segundo_token.lexem != "NULL":
                    raise exc.SemanticoTokensIncompatibles(tokens=[primer_token, segundo_token])

                self.tabla_simbolos[primer_token.lexem]["VALOR"]["CAMPO"]["VALOR"] = "NULL"
                self.tabla_simbolos[primer_token.lexem]["VALOR"]["APUNTADOR"]["VALOR"] = "NULL"

            self.get_next_token()
            self.E()
        
        elif self.predict(["SUMA", "RESTA", "DIV", "MULTI", "MOD"]):
            tercer_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.E_VIII(primer_token=primer_token, segundo_token=segundo_token, tercer_token=tercer_token)
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["PUNTO_COMA", "SUMA", "RESTA", "DIV", "MULTI", "MOD"])
  
    def E_VI(self, primer_token : Token, segundo_token : Token):
        self.match(["ASIGNA"])

        self.get_next_token()
        self.E_IX(primer_token=primer_token, segundo_token=segundo_token)

    def E_VII(self, primer_token : Token, segundo_token : Token, tercer_token : Token):
        if self.predict(["IDENTIFICADOR"]):
            """AQUI TERMINA LA EXPRESION DE TIPO ID = ID OP ID """
            cuarto_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            print(f"{primer_token.lexem} = {segundo_token.lexem} {tercer_token.lexem} {cuarto_token.lexem}")

            self.get_next_token()
            self.E()
        
        elif self.predict(["INT", "CHAR", "STRING", "NULL"]):
            """AQUI TERMINA LA EXPRESION DE TIPO: ID = ID OP VALOR """
            cuarto_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            print(f"{primer_token.lexem} = {segundo_token.lexem} {tercer_token.lexem} {cuarto_token.lexem}")

            self.get_next_token()
            self.E()
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["IDENTIFICADOR", "INT", "CHAR", "STRING", "NULL"])

    def E_VIII(self, primer_token : Token, segundo_token : Token, tercer_token : Token):
        """ AQUI SE ENCUENTRA EL FINAL DE LA EXPRESION: ID = VALOR OP ID """
        if self.predict(["IDENTIFICADOR"]):
            cuarto_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            print(f"{primer_token.lexem} = {segundo_token.lexem} {tercer_token.lexem} {cuarto_token.lexem}")

            self.get_next_token()
            self.E()

        elif self.predict(["INT", "STRING", "CHAR", "NULL"]):
            """ AQUI SE ENCUENTRA EL FINAL DE LA EXPRESION ID = VALOR OP VALOR  """
            cuarto_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            print(f"{primer_token.lexem} = {segundo_token.lexem} {tercer_token.lexem} {cuarto_token.lexem}")
            
            self.get_next_token()
            self.E()
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["IDENTIFICADOR", "INT", "STRING", "CHAR", "NULL"])

    def E_IX(self, primer_token : Token, segundo_token : Token):
        if self.predict(["IDENTIFICADOR"]):
            """AQUI TERMINA LA ASIGNACION DE UN ID A UNA ESTRUCTRA : ID.ID = ID"""
            tercer_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            print(f"{primer_token.lexem}.{segundo_token.lexem} = {tercer_token.lexem}")

            self.get_next_token()
            self.E()

        elif self.predict(["INT", "CHAR", "STRING", "NULL"]):
            """AQUI TERMINA LA ASIGNACION DE UN VALOR A UNA ESTRUCTURA : ID.ID = VALOR"""
            tercer_token = copy.deepcopy(self.token_actual)

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            print(f"{primer_token.lexem}.{segundo_token.lexem} = {tercer_token.lexem}")

            self.get_next_token()
            self.E()
        else:
            raise exc.SemanticoTokenIncorrecto(token_actual=self.token_actual, tokens=["IDENTIFICADOR", "INT", "CHAR", "STRING", "NULL"])

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
        else:
            raise Exception
    