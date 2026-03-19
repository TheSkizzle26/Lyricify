class Line:
    def __init__(self, time: float, text: str):
        self.time = time
        self.text = text

    def char_idx(self, t: float):
        return int(t * (len(self.text)-1))