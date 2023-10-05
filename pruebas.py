from automata_reader import table_reader as tr

import os

def main():
    tabla = tr.table_reader(f"{os.getcwd()}/tablita.txt")
    
    for fila in tabla.tabla:
        print(fila)
    print("")
    print("alfabeto: ", tabla.alfabeto)
    print("estados:", tabla.estados)
    print("estado inicial", tabla.estado_inicial)
    print("estados finales:", tabla.estados_finales)
    
    print("transiciones")
    for key in tabla.transiciones.keys():
        print("estado: ", key, tabla.transiciones.get(key))

    print("tokens", tabla.tokens)

    print("retrocesos", tabla.retrocesos)

if __name__ == "__main__":
    main()
