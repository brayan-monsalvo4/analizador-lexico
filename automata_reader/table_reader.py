import string

class table_reader:
    def __init__(self):
        self.alfabeto : set[str]
        self.estados : list[str]
        self.estado_inicial : str
        self.estados_finales : set[str]
        self.simbolo : str
        self.transiciones : dict[ str : dict[ str : str ] ] = dict()
        self.tabla : list[ list[str] ]
        self.tokens : dict[str : str] = dict()
        self.retrocesos : dict[str : int] = dict()

    def leer_datos(self, path : str):
        with open(path, "r") as file:
            """lee el estado inicial y el simbolo de valor nulo"""
            self.estado_inicial = file.readline().strip(string.whitespace)     
            self.simbolo = file.readline().strip(string.whitespace)

            tabla : list[ list[str] ] = list()      
            for linea in file.readlines():
                """limpia los caracteres del archivo quitando espacios en blanco y saltos de linea a los costados, pero no los quita por
                completo"""
                linea = linea.strip(string.whitespace)

                """filtra los elementos anteriores, guardando unicamente los elementos que no son una cadena vacia '', resultado de 
                linea.split(' ')"""
                tabla.append( list(filter( lambda celda: celda != "" , linea.split(" "))) )

            self.tabla = tabla
            
            """lee la primera fila de la tabla, e ignora la primer y ultimas dos casillas (retr y token), resultando en el alfabeto"""
            self.alfabeto = [ letra for letra in self.tabla[0][1:-2 ]]

            """si encuentra los conjutos de los numeros, letras, letras en minusculas o mayusculas (digits, letters, ...)reemplaza
            el nombre del conjunto por todos sus elementos"""
            self.alfabeto.extend(list(string.digits)) if "digits" in self.alfabeto else  None
            self.alfabeto.extend(list(string.ascii_letters)) if "letters" in self.alfabeto else None
            self.alfabeto.extend(list(string.ascii_lowercase)) if "letters_lowercase" in self.alfabeto else None
            self.alfabeto.extend(list(string.ascii_uppercase)) if "letters_uppercase" in self.alfabeto else None
            self.alfabeto.extend(list(string.whitespace)) if "otros" in self.alfabeto else None


            self.alfabeto.remove("digits") if "digits" in self.alfabeto else None
            self.alfabeto.remove("letters") if "letters" in self.alfabeto else None
            self.alfabeto.remove("letters_lowercase") if "letters_lowercase" in self.alfabeto else None
            self.alfabeto.remove("letters_uppercase") if "letters_uppercase" in self.alfabeto else None
            self.alfabeto.remove("otros") if "otros" in self.alfabeto else None

            """lee la primer columna a partir de la segunda fila (la primera fila contiene el alfabeto)"""
            self.estados = [letra[0] for letra in self.tabla[1:] ]

            """lee la primer columna como antes, pero ahora guarda el estado si es que todas las transiciones de dicho 
            estado son iguales al simbolo de valor nulo"""
            self.estados_finales = [fila[0] for fila in self.tabla[1:] if len(fila[1:-2]) == fila[1:-2].count(self.simbolo)]
            
            """recorre toda la tabla, pero empezando a leer las transiciones desde [1][1] (ignorando columna de estados y fila del alfabeto)"""
            #filas
            for i in range(1, len(self.tabla)):
                estado_actual : str = self.tabla[i][0]
                transicion : dict[str, str] = dict()
                
                #columnas
                for j in range(1, len(self.tabla[i])-2):
                    simbolo_actual : str = self.tabla[0][j]

                    simbolo_actual = string.ascii_letters if simbolo_actual == "letters" else simbolo_actual
                    simbolo_actual = string.ascii_lowercase if simbolo_actual == "letters_lowercase" else simbolo_actual
                    simbolo_actual = string.ascii_uppercase if simbolo_actual == "letters_uppercase" else simbolo_actual
                    simbolo_actual = string.digits if simbolo_actual == "digits" else simbolo_actual
                    simbolo_actual = string.whitespace if simbolo_actual == "otros" else simbolo_actual

                    estado_siguiente : str = self.tabla[i][j]

                    """crea un diccionario con la transicion del estado actual y el simbolo actual
                     si es que dicha transicion no es igual al simbolo de valor nulo"""
                    transicion.update({ simbolo_actual : estado_siguiente }) if not estado_siguiente == self.simbolo  else transicion.update({})
                
                """se guarda la lista de transiciones del estado actual si es que dicha lista no es vacia"""
                if bool(transicion):
                    self.transiciones.update({ estado_actual : transicion }) 

            """busca entre todas las filas a partir de la segunda"""
            for fila in self.tabla[1:]:

                """si el estado en dicha fila es final"""
                if fila[0] in self.estados_finales:
                    """guarda el estado y el token si dicho token no es igual al simbolo de valor nulo"""
                    self.tokens.update({ fila[0] : fila[-1] }) if fila[-1] != self.simbolo else self.tokens.update({})

                    """si ademas dicho estado tiene retroceso, o el retroceso es distinto al simbolo de valor nulo"""
                    if fila[-2] != self.simbolo:
                        self.retrocesos.update( { fila[0] : int(fila[-2]) } )
                

