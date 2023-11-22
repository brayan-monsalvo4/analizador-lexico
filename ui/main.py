import customtkinter as ctk
from tkinter import messagebox as mb
from automata_reader import table_reader as tr
from dfa import dfa
from dfa import token
import os
import datetime
class PantallaPrincipal:

    def __init__(self):
        self.__app = ctk.CTk()
        self.__app.geometry("1200x800")
        self.__table_reader : tr.table_reader = tr.table_reader()
        self.__path_tabla_automata : str = ""
        self.__automata : dfa.Dfa = dfa.Dfa()
        self.__archivo_path : str = ""
        

        ctk.set_default_color_theme("dark-blue")

        self.__declaracion_elementos()

        self.__configuracion_elementos()

        self.__posicionar_elementos()


    def __declaracion_elementos(self):
        """Hay 2 frames principales, el frame para el editor y la salida, cada frame contiene un subframe donde se 
        colocan los botones de acciones, cada frame tiene sus respectivos botones"""
        self.__frame_editor = ctk.CTkFrame(master=self.__app)
        self.__frame_output = ctk.CTkFrame(master=self.__app)

        self.__frame_botones_archivo = ctk.CTkFrame(master=self.__frame_editor)
        self.__frame_botones_output = ctk.CTkFrame(master=self.__frame_output)

        self.__boton_abrir_archivo = ctk.CTkButton(master=self.__frame_botones_archivo, text="Abrir archivo", command=self.__abrir_archivo)
        self.__boton_guardar_archivo = ctk.CTkButton(master=self.__frame_botones_archivo, text="Guardar archivo", command=self.__guardar_archivo)
        self.__boton_limpiar_editor = ctk.CTkButton(master=self.__frame_botones_archivo, text="Limpiar editor", command=lambda: self.__limpiar_text_box(self.__text_editor))

        self.__boton_run = ctk.CTkButton(master=self.__frame_botones_output, text="RUN", command=self.__run)
        self.__boton_step = ctk.CTkButton(master=self.__frame_botones_output, text="Step", command=self.__step)
        self.__boton_reiniciar = ctk.CTkButton(master=self.__frame_botones_output, text="Reiniciar", command=self.__reiniciar)
        self.__boton_cargar_automata = ctk.CTkButton(master=self.__frame_botones_output, text="Cargar AFD", command=self.__cargar_automata)
        self.__label_ruta_afd = ctk.CTkLabel(master=self.__frame_botones_output, text="---")

        self.__text_editor = ctk.CTkTextbox(master=self.__frame_editor, font=("Console", 18))
        self.__text_output = ctk.CTkTextbox(master=self.__frame_output, font=("Console", 18))
        self.__text_log = ctk.CTkTextbox(master=self.__app, font=("Console", 18))

    def __configuracion_elementos(self):
        """La configuracion inicial que se le da es principalmente a las filas y columnas, rowconfigure y columnconfigure con el argumento
        weight=1 indica la prioridad que tiene dicha fila de expandirse cuando se redimensiona el contenedor"""
        self.__app.rowconfigure(0, weight=1)
        self.__app.columnconfigure(0, weight=1)
        self.__app.columnconfigure(1, weight=1)
        #self.__frame_log = ctk.CTkFrame(master=self.__app)

        self.__frame_editor.rowconfigure(1, weight=1)
        self.__frame_editor.columnconfigure(0, weight=1)

        self.__frame_botones_output.rowconfigure(0, weight=1)
        self.__frame_output.rowconfigure(1, weight=1)
        self.__frame_output.columnconfigure(0, weight=1)

        self.__frame_botones_archivo.rowconfigure(0, weight=1)
        self.__frame_botones_archivo.columnconfigure(0, weight=1)
        self.__frame_botones_archivo.columnconfigure(1, weight=1)
        self.__frame_botones_archivo.columnconfigure(2, weight=1)

        self.__frame_botones_output.rowconfigure(0, weight=1)
        self.__frame_botones_output.rowconfigure(1, weight=1)
        self.__frame_botones_output.columnconfigure(0, weight=1)
        self.__frame_botones_output.columnconfigure(1, weight=1)
        self.__frame_botones_output.columnconfigure(2, weight=1)

        #"""inicialmente estan desactivados los TextBox del output y el log"""
        #self.__text_log.configure(state="disabled")
        #self.__text_output.configure(state="disabled")

    def __posicionar_elementos(self):
        """al usar el layout manager grid, la ventana o contenedor actua como una tabla, en donde cada elemento se posiciona
        en una determinada fila y columna, con la posibilidad de que dicho elemento pueda expandise n filas o columnas, ademas de 
        indicar hacia que lado debe alinearse o 'pegarse' (sticky) el elemento"""
        self.__frame_editor.grid(column=0, row=0, padx=20, pady=20, sticky="w e n s")
        self.__frame_output.grid(column=1, row=0, padx=20, pady=20, sticky="w e n s")
        self.__text_log.grid(column=0, row=1, columnspan=2 , padx=20, pady=20 ,sticky="w e n s")

        #self.__frame_log.grid(column=0 , row=1, columnspan=2, padx=20, pady=20, sticky="w e")

        self.__frame_botones_archivo.grid(column=0,row=0, pady=10, sticky="w e")
        self.__frame_botones_output.grid(column=0, row=0, pady=10, sticky="w e")

        self.__boton_abrir_archivo.grid(column=0, row=0, padx=5)
        self.__boton_guardar_archivo.grid(column=1, row=0, padx=5)
        self.__boton_limpiar_editor.grid(column=2, row=0, padx=5)

        self.__boton_cargar_automata.grid(column=0, row=0, padx=5, pady=5)
        self.__label_ruta_afd.grid(column=1, row=0, columnspan=2, padx=5, pady=5)
        self.__boton_run.grid(column=0, row=1, padx=5)
        self.__boton_step.grid(column=1, row=1, padx=5)
        self.__boton_reiniciar.grid(column=2, row=1, padx=5)

        self.__text_editor.grid(column=0, columnspan=3, row=1, rowspan=8, sticky="w e s n", pady=5)
        self.__text_output.grid(column=0, row=1, columnspan=3, rowspan=8,  sticky="w e s n", pady=5)

    def iniciar(self):
        self.__app.mainloop()

    def __abrir_archivo(self):
        path = ctk.filedialog.askopenfilename(
            title="Abrir archivo",
            initialdir=os.getcwd(),
            filetypes=[('All files', '*.*')]
        )
        
        if not self.__es_archivo_texto(path):
            mb.showerror(title="Error", message="El archivo seleccionado no es de texto plano!")
            return ""
        
        with open(path, "r") as file:
            self.__limpiar_text_box(self.__text_editor)
            self.__archivo_path = path
            self.__text_editor.insert(ctk.END, file.read())
            self.__automata.cargar_archivo_fuente(path)

    def __cargar_automata(self):
        path = ctk.filedialog.askopenfilename(
            title="Abrir archivo",
            initialdir=os.getcwd(),
            filetypes=[('Archivos JFLAP', '*.jff')]
        )

        #if not self.__es_archivo_texto(path=path):
        #    mb.showerror(title="Error", message="El archivo seleccionado no es de texto plano!")
        #    return ""
        print(path)
        self.__path_tabla_automata = path        
        
        try:
            self.__table_reader.leer_datos(path_xml=path)
            self.__label_ruta_afd.configure(text=path)
            self.__automata.cargar_datos(self.__table_reader)

            print(self.__automata.transiciones)

        except Exception as e:
            self.__insertar_texto(self.__text_log, f"Automata incorrecto: {datetime.datetime.now().time().strftime('%X')} ", reemplazar=False, salto_linea=True)
            mb.showerror(title="Error", message="Tabla de transicion incorrecta!")

    def __limpiar_text_box(self, textbox : ctk.CTkTextbox):
        #if textbox.cget("state") == "disabled":
        #    textbox.configure(state="normal")
        #    textbox.delete("0.0", ctk.END)
        #    textbox.configure(state="disabled")
        #    return
        
        textbox.delete("0.0", ctk.END)

    def __insertar_texto(self, textbox: ctk.CTkTextbox, texto: str, reemplazar: bool, salto_linea: bool):
        textbox.configure(state="normal")
        
        if reemplazar:
            self.__limpiar_text_box(textbox=textbox)
        textbox.insert(ctk.END, text=texto) if not salto_linea else textbox.insert(ctk.END, text=f"{texto}\n")     
    
    def __guardar_archivo(self):
        try:
            if len(self.__text_editor.get("1.0", "end-1c")) == 0:
                mb.showerror(title="Error", message="El editor esta vacio!")
                raise Exception

            filename = ctk.filedialog.asksaveasfile(initialdir=os.getcwd(), mode="w")
            filename.write(self.__text_editor.get("0.0", "end-1c"))

        except Exception as e:
            print(e)

    def __es_archivo_texto(self, path: str) -> bool:
        try:
            file = open(path, "r")
            file.readlines()
            file.close()
            return True
        except Exception:
            
            return False
        
    def __run(self):
        if not self.__path_tabla_automata:
            mb.showerror(title="Error", message="No hay cargado ningun automata!")  
            return 

        if not self.__archivo_path:
            mb.showerror(title="Error", message="No ha abierto ningun archivo de texto!")  
            return

        try:
            if len(self.__text_editor.get("0.0", "end-1c")) == 0:
                mb.showerror(title="Error", message="El editor esta vacio!")
                raise Exception 
            
            self.__limpiar_text_box(textbox=self.__text_output)
            self.__automata.cargar_archivo_fuente(path=self.__archivo_path)
            self.__automata.reiniciar()

            while tokencito:= self.__automata.get_token():
                self.__insertar_texto(textbox=self.__text_output, texto=tokencito, reemplazar=False, salto_linea=True)

        except Exception as e:
            self.__insertar_texto(self.__text_log, texto=f"{e}: {self.__automata.get_posicion_actual()}", salto_linea=True, reemplazar=False)

    
    def __reiniciar(self):
        self.__automata.reiniciar()
        self.__limpiar_text_box(textbox=self.__text_output)

    def __step(self):
        if not self.__path_tabla_automata:
            mb.showerror(title="Error", message="No hay cargado ningun automata!")
            return

        if not self.__archivo_path:
            mb.showerror(title="Error", message="No ha abierto ningun archivo de texto!")  
            return
        
        try:
            if len(self.__text_editor.get("0.0", "end-1c")) == 0:
                mb.showerror(title="Error", message="El editor esta vaio!")
                raise Exception
            
            tokencito = self.__automata.get_token()
            
            if token:
                self.__insertar_texto(textbox=self.__text_output, texto=tokencito, reemplazar=False, salto_linea=True)
            
        except Exception as e:
            self.__insertar_texto(textbox=self.__text_log, texto=e, reemplazar=False, salto_linea=True)
