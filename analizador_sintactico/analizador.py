from dfa.token import Token
from dfa.dfa import Dfa
from exceptions.exceptions import TokenIncorrecto
from enum import Enum

class analizador:
    def __init__(self, analex : Dfa):
        self.token_actual : Token = None
        self.lexic : Dfa = analex
        self.tabla_simbolos : dict = dict()

        self.tabla_constantes : dict = dict()
        self.tabla_variables : dict = dict()
    
    def guardar_constante(self, identificador):
        if identificador in self.tabla_constantes.keys() or identificador in self.tabla_simbolos.keys():
            raise Exception

        self.tabla_constantes.update( { identificador : self.token_actual.lexem } )
        self.tabla_simbolos.update( { identificador : self.token_actual.type } )

    def guardar_variable(self, type : str):
        if (self.token_actual.lexem in self.tabla_variables) or (self.token_actual.lexem in self.tabla_simbolos.keys()):
            raise Exception
        
        self.tabla_variables.update( { self.token_actual.lexem : None } )
        self.tabla_simbolos.update( { self.token_actual.lexem : type } )

    def get_next_token(self):
        self.token_actual = self.lexic.get_token()
        while self.token_actual.type == "SEPARADOR": 
            self.token_actual = self.lexic.get_token()

        #print(f"token leido : <{self.token_actual.type}:{self.token_actual.lexem}>")

    def match(self, tkns : list[str]):
        #print(f"haciendo match de {self.token_actual.type} en {tkns}")
        if not self.token_actual.type in tkns:
            raise Exception
        
    def predict(self, tkns : list[str]) -> bool:
        return self.token_actual.type in tkns

    def S (self):
        self.get_next_token()
        self.match(["PROGRAM"])

        self.get_next_token()
        self.match(["IDENTIFICADOR"])

        self.tabla_simbolos.update(  { self.token_actual.lexem : self.token_actual.type }  )

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

        print(self.token_actual)
        self.match(["END"])

        print("programa aceptado xd")
    
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
            self.VALOR()

            self.guardar_constante(identificador=id)
            
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
            
            self.get_next_token()
        if self.predict(["BEGIN", "VARS"]):
            return

    def CC(self):
        if self.predict(["IDENTIFICADOR"]):
            nombre_estructura = self.token_actual.lexem

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

            self.get_next_token()
            self.match(["LLAV_C"])

            print(f"estructura: {nombre_estructura} = {tipo_1} {campo_1} ; {tipo_2} {campo_2}")

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
        if self.predict(["INT", "CHAR", "STRING", "POINTER"]):
            tipo = self.token_actual.type

            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            self.guardar_variable(type=tipo)

            self.get_next_token()
            self.DPP(type=tipo)
            
            self.match("PUNTO_COMA") 

            self.get_next_token()
            self.DP()  
        
        elif self.predict(["BEGIN"]):
            return
        else:
            raise Exception
        
    def DPP(self, type : str):
        if self.predict(["COMA"]):
            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            self.guardar_variable(type)
            
            self.get_next_token()
            self.DPP(type)
        elif self.predict(["PUNTO_COMA"]):
            return
        else:
            raise Exception

    def E(self):
        if self.predict(["IDENTIFICADOR"]):
            id_1 = self.token_actual.lexem

            self.get_next_token()
            self.EP(id_1)
        
        elif self.predict(["READ"]):
            self.get_next_token()
            self.READ()
        
        elif self.predict(["WRITE"]):
            self.get_next_token()
            self.WRITE()

        elif self.predict(["WHILE"]):
            self.get_next_token()
            self.WHILE()

        elif self.predict(["IF"]):
            self.get_next_token()
            self.IF()
        
        elif self.predict(["END", "ELSE"]):
            return
        else:
            raise Exception
    
    def EP(self, id_1):
        if self.predict(["PUNTO"]):
            self.get_next_token()
            self.match(["IDENTIFICADOR"])

            id_2 = self.token_actual.lexem

            self.get_next_token()
            self.match(["ASIGNA"])

            self.get_next_token()
            tipo_valor = self.VALOR()
            valor = self.token_actual.lexem

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            print(f"Apuntador: {id_1}.{id_2} = {tipo_valor} {valor} ;")

            self.get_next_token()
            self.E()
        elif self.predict(["ASIGNA"]):
            self.get_next_token()
            self.EPP(id_1)
        else:
            raise Exception

    def EPP(self, variable):
        if self.predict(["IDENTIFICACION"]):
            operando_1 = self.token_actual.lexem

            self.get_next_token()
            operacion = self.OPMA()

            self.get_next_token()
            operando_2 = self.M()

            self.get_next_token()
            self.match(["PUNTO_COMA"])

            print(f"expresion: {variable} = {operando_1} {operacion} {operando_2}")

            self.get_next_token()
            self.E()
        elif self.predict(["INT", "CHAR", "STRING", "NULL"]):
            self.match(["INT", "CHAR", "STRING", "NULL"])
            tipo_dato = self.VALOR()
            
            self.get_next_token()
            self.EPPP(primer_operando=self.token_actual.lexem, variable=variable)
        
        else:
            raise Exception
        
    def EPPP(self, variable ,primer_operando):
        if self.predict(["PUNTO_COMA"]):
            self.match(["PUNTO_COMA"])

            print(f"asignacion : {variable} = {primer_operando}")

            self.get_next_token()
            self.E()
        
        elif self.predict(["SUMA", "RESTA", "MULTI", "DIV"]):
            operador = self.OPMA()

            self.get_next_token()
            operando_2 = self.M()

            self.get_next_token()
            self.match(["PUNTO_COMA"])
            print(f"expresion: {variable} = {primer_operando} {operador} {operando_2}")
            self.get_next_token()
            self.E()
        else:
            raise Exception

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
        cosa_a_imprimir = self.M()
        
        self.get_next_token()
        self.match(["PAR_C"])

        self.get_next_token()
        self.match(["PUNTO_COMA"])

        print(f"write : ({cosa_a_imprimir})")

        self.get_next_token()
        self.E()

    def IF(self):
        self.match(["PAR_A"])

        self.get_next_token()
        res = self.CON()

        self.get_next_token()
        self.match(["PAR_C"])

        self.get_next_token()
        self.match(["THEN"])

        self.get_next_token()
        self.E()

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
        self.get_next_token()
        self.match(["PAR_A"])

        self.get_next_token()
        self.CON()

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
            print("entro con")
            operando_1 = self.M()

            self.get_next_token()
            operacion = self.OPCO()

            self.get_next_token()
            operando_2 = self.M()

            print(f"condicion: {operando_1} {operacion} {operando_2}")
            print("salio con")
            return True

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
            return self.token_actual.lexem
        elif self.predict(["INT", "CHAR", "STRING", "NULL"]):
            self.VALOR()
            return self.token_actual.lexem
        else:
            raise Exception
    