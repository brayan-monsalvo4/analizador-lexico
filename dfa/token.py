

class Token:
    def __init__(self, type: str, lexem : str, coordinates: tuple[int, int]):
        self.type : str = type
        self.lexem : str = lexem
        self.coordinates : tuple[int, int] = coordinates


    def __str__(self) -> str:
        return f"<TYPE:{self.type},  LEXEM: {self.lexem},  POSITION: {self.coordinates}>"