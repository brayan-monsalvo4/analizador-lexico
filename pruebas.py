from automata_reader import table_reader as tr
from analizador_sintactico import analizador
from dfa import dfa, token
import os
import string
import time
from prettytable import PrettyTable

def main():
    start_time = time.time()

    tabla = tr.table_reader()
    tabla.leer_datos(path_xml=f"{os.getcwd()}/automata_interprete_sin_notas.jff")
    
    automata = dfa.Dfa()
    analizer = analizador.analizador(analex=automata)
    automata.cargar_datos(tabla=tabla)
    automata.cargar_archivo_fuente(path=f"{os.getcwd()}/archivo.txt")

    analizer.S()

    tabla_simbolos = analizer.tabla_simbolos
    tabla_variables = analizer.tabla_variables
    tabla_constantes = analizer.tabla_constantes

    tabla_1 = PrettyTable(["token", "tipo"])
    tabla_2 = PrettyTable(["id", "valor"])
    tabla_3 = PrettyTable(["id", "valor"])

    for campo, valor in tabla_simbolos.items():
        tabla_1.add_row([campo, valor])

    for campo, valor in tabla_variables.items():
        tabla_2.add_row([campo, valor])
    
    for campo, valor in tabla_constantes.items():
        tabla_3.add_row([campo, valor])

    print("simbolos:")
    print(tabla_1)
    
    print("variables:")
    print(tabla_2)

    print("constantes:")
    print(tabla_3)

    end_time = time.time()  
    elapsed_time = end_time - start_time  # Calcular el tiempo transcurrido

    print(f"Tiempo de ejecución: {elapsed_time} segundos")
        
if __name__ == "__main__":
    main()
