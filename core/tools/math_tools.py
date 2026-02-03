import numpy as np
from typing import Tuple

def calculate_angle(
    base: Tuple[float, float],
    test: Tuple[float, float],
    reference_axis: str = 'x'
) -> float:
    """
    Calcula el ángulo entre el vector formado por dos puntos (base → test) y un eje de referencia.

    El ángulo se devuelve en grados, normalizado en el rango [-180°, 180°], positivo en sentido antihorario.

    Args:
        base (Tuple[float, float]): Coordenadas (x, y) del punto base.
        test (Tuple[float, float]): Coordenadas (x, y) del punto test.
        reference_axis (str, optional): Eje de referencia para el cálculo ('x' o 'y'). Por defecto 'x'.

    Returns:
        float: Ángulo en grados entre el vector y el eje de referencia, en el rango [-180°, 180°].

    Raises:
        TypeError: Si las entradas no son tuplas de dos elementos numéricos.
        ValueError: Si las coordenadas contienen NaN o si el eje de referencia no es válido.
    """
    # Validación de tipo y longitud
    if not (isinstance(base, tuple) and isinstance(test, tuple)):
        raise TypeError("Los puntos deben ser tuplas (x, y)")
    if len(base) != 2 or len(test) != 2:
        raise ValueError("Cada punto debe tener dos coordenadas (x, y)")

    # Validación de contenido numérico
    if any(coord is None or not isinstance(coord, (int, float)) for coord in base + test):
        raise TypeError("Las coordenadas deben ser valores numéricos")

    # Cálculo del vector
    dx = test[0] - base[0]
    dy = test[1] - base[1]

    # Ángulo respecto al eje elegido
    if reference_axis == 'x':
        angle_rad = np.arctan2(dy, dx)
    elif reference_axis == 'y':
        angle_rad = np.arctan2(dx, dy)
    else:
        raise ValueError("El eje de referencia debe ser 'x' o 'y'")

    # Conversión a grados y normalización [-180, 180]
    angle_deg = np.degrees(angle_rad)
    if angle_deg > 180:
        angle_deg -= 360
    elif angle_deg < -180:
        angle_deg += 360

    return angle_deg
    