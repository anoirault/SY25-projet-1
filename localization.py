from typing import Dict, Tuple

from Anchor import Anchor


def trilaterate(
    anc_dist_A: Tuple[Anchor, float],
    anc_dist_B: Tuple[Anchor, float],
    anc_dist_C: Tuple[Anchor, float],
) -> Tuple[float, float]:
    anc_A, dist_A = anc_dist_A
    anc_B, dist_B = anc_dist_B
    anc_C, dist_C = anc_dist_C

    xa, ya = anc_A.position
    xb, yb = anc_B.position
    xc, yc = anc_C.position

    a = 2 * (xb - xa)
    b = 2 * (yb - ya)
    c = 2 * (xc - xa)
    d = 2 * (xc - xa)

    alpha = dist_A**2 - dist_B**2 + xb**2 - xa**2 + yb**2 - ya**2
    beta = dist_A**2 - dist_C**2 + xc**2 - xa**2 + yc**2 - ya**2

    var = a * d - b * c
    if var == 0:
        return 0, 0

    x = 1 / var * (alpha * d - beta * b)
    y = 1 / var * (-alpha * c + beta * a)

    return x, y

def min_max(
    anchor_distances: Dict[Anchor, float]
) -> Tuple[float, float, float, float]:
    min_x, min_y, max_x, max_y = (
        -100000000000000000.0,
        -100000000000000000.0,
        100000000000000000.0,
        100000000000000000.0,
    )

    for anchor, distance in anchor_distances.items():
        anc_x, anc_y = anchor.position

        min_x = max(min_x, anc_x - distance)
        min_y = max(min_y, anc_y - distance)

        max_x = min(max_x, anc_x + distance)
        max_y = min(max_y, anc_y + distance)

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0

    width = max_x - min_x
    height = max_y - min_y

    return center_x, center_y, width, height