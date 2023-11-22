from automata_reader import table_reader as tr
from dfa import dfa, token
import os
import string
import time

def main():
    start_time = time.time()

    tabla = tr.table_reader()
    tabla.leer_datos(path_xml=f"{os.getcwd()}/automata_interprete_sin_notas.jff")
    
    automata = dfa.Dfa()

    automata.cargar_datos(tabla=tabla)
    automata.cargar_archivo_fuente(path=f"{os.getcwd()}/archivo.txt")

    #with open("resultado", "w") as file:
    while token := automata.get_token():
        if token.type != "SEPARADOR":
            print(token)
    print(automata.get_token())
    print(automata.get_token())
    print(automata.get_token())
    automata.reiniciar()
    print(automata.get_token())
    end_time = time.time()  
    elapsed_time = end_time - start_time  # Calcular el tiempo transcurrido

    print(f"Tiempo de ejecución: {elapsed_time} segundos")
        
if __name__ == "__main__":
    main()
