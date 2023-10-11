from automata_reader import table_reader as tr
from dfa import dfa
import os
import string

def main():
    tabla = tr.table_reader()
    tabla.leer_datos(f"{os.getcwd()}/tablita.txt")
    print(tabla.transiciones)
    print()
    #
#
    #automata = dfa.Dfa(estados=set(tabla.estados), alfabeto=tabla.alfabeto, estados_finales=set(tabla.estados_finales),
    #                   estado_inicial=tabla.estado_inicial, transiciones=tabla.transiciones, tokens=tabla.tokens, retr=tabla.retrocesos)
#
#
    ##print(automata.acepta_cadena("1245 4 5 "))
    ##print(automata.transiciones)
#
    #while True:
    #    token = automata.get_token(f"{os.getcwd()}/texto.txt")
    #    if not token:
    #        break
    #    print(token)                

    automata = dfa.Dfa()
    automata.cargar_datos(tabla=tabla)

    automata.cargar_archivo_fuente(path=f"{os.getcwd()}/texto.txt")
    while True:
        token = automata.get_token()
        if not token:
            break
        print(token)

if __name__ == "__main__":
    main()
