class Frame:

    def __init__(self, frame: str, row: int, column: int):
        self.frame = frame
        self.row = row
        self.column = column

    def __call__(self):
        return self.frame
