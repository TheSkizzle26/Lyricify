import math


def ease_out_quart(x: float):
    return 1 - math.pow(1 - x, 4)

def ease_in_out_quint(x: float):
    return (16 * x * x * x * x * x) if x < 0.5 else (1 - math.pow(-2 * x + 2, 5) / 2)

def ease_in_out_quad(x: float):
    return (2 * x * x) if x < 0.5 else (1 - math.pow(-2 * x + 2, 2) / 2)