import string
import re
import xmltodict
import json

class table_reader:
    def __init__(self):
        self.estados : set[str]
        self.estado_inicial : str
        self.estados_finales : set[str]
        self.transiciones : dict[ str : dict[ str : str ] ] = dict()
        self.tokens : dict[str : str] = dict()
        self.retrocesos : dict[str : int] = dict()
        self.palabras_reservadas : set[str]

    def leer_datos(self, path_xml):
        with open(path_xml, "rb") as file:
            datos_xml = xmltodict.parse(file)

        self.palabras_reservadas = set( datos_xml.get("structure").get("automaton").get("note").get("text").split("\n") )
        
        lista_estados : list[str] = list()
        lista_estados_finales : list[str] = list()
        estados_temporal : dict[str, str] = dict()

        for estado in datos_xml.get("structure").get("automaton").get("state"):
            lista_estados.append(estado.get("@name"))

            estados_temporal.update({estado.get("@id") : estado.get("@name")})

            if "initial" in estado.keys():
                self.estado_inicial = estado.get("@name")
            if "final" in estado.keys():
                lista_estados_finales.append(estado.get("@name"))
                label = estado.get("label")

                token, retroceso = label.split(",")

                token = token.split(":")
                retroceso = retroceso.split(":")

                token = token[1].strip()
                retroceso = retroceso[1].strip()

                self.tokens.update( { estado.get("@name") : token } )
                self.retrocesos.update( { estado.get("@name") : int(retroceso) } )
        
        
        if not isinstance(datos_xml.get("structure").get("automaton").get("transition"), list):
            id_inicial : str = datos_xml.get("structure").get("automaton").get("transition").get("from")
            id_siguiente :  str = datos_xml.get("structure").get("automaton").get("transition").get("to")

            estado_inicial : str = estados_temporal.get(id_inicial)
            estado_siguiente : str = estados_temporal.get(id_siguiente)

            simbolo : str = datos_xml.get("structure").get("automaton").get("transition").get("read")

            self.transiciones.update( { estado_inicial : dict() } )
            self.transiciones.get(estado_inicial).update( { simbolo : estado_siguiente } )

        else:
            for transicion in datos_xml.get("structure").get("automaton").get("transition"):
                estado_inicial : str = estados_temporal.get(transicion.get("from"))
                estado_siguiente : str = estados_temporal.get(transicion.get("to"))
                simbolo : str = transicion.get("read")

                if not estado_inicial in self.transiciones.keys():
                    self.transiciones.update( { estado_inicial : dict() } )

                self.transiciones.get(estado_inicial).update( { simbolo : estado_siguiente } )

        self.estados = set(lista_estados)
        self.estados_finales = set(lista_estados_finales)