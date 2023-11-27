

class Token:
    def __init__(self, type: str, lexem : str, coordinates: tuple[int, int]):
        self.type : str = type
        self.lexem : str = lexem
        self.final_coordinates : tuple[int, int] = coordinates
        inicio, fin = coordinates

        self.initial_coordinates : tuple[int, int] = (inicio, fin - len(lexem))


    def __str__(self) -> str:
        return f"<TYPE:{self.type},  LEXEM: {self.lexem}, INITIAL POSITION: {self.initial_coordinates}, FINAL POSITION: {self.final_coordinates} >"