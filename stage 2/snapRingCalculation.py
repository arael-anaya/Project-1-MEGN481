"""
Solve for required shaft diameter to meet target FoS.

Units:
- Sy in psi
- M, T in in-lbf
- V in lbf
- d in inches
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np
import keywayCalculations

standard_od = [
    0.25,
    0.28125,
    0.3125,
    0.34375,
    0.375,
    0.40625,
    0.4375,
    0.46875,
    0.5,
    0.5625,
    0.59375,
    0.625,
    0.6875,
    0.75,
    0.78125,
    0.8125,
    0.84375,
    0.875,
    0.9375,
    0.984375,
    1.0,
    1.0625,
    1.125,
    1.1875,
    1.25,
    1.3125,
    1.375,
    1.4375,
    1.5,
    1.5625,
    1.625,
    1.6875,
    1.75,
    1.8125,
    1.875,
    1.96875,
    2.0,
    2.0625,
    2.125,
    2.15625,
    2.25,
    2.3125,
    2.375,
    2.4375,
    2.5,
    2.559,
    2.625,
    2.6875,
    2.75,
    2.875
]



def von_mises_stress(d_out, d_in, V, M, T, Kt, Kts):
    pi = np.pi

    J = (pi / 32) * (d_out**4 - d_in**4)
    I = (pi / 64) * (d_out**4 - d_in**4)
    c = d_out / 2

    sigma_b = Kt * (c * M / I)
    tau_t = Kts * (c * T / J)

    tau_v = 16 * V / (3 * pi * (d_out**4 - d_in**4))

    tau_combined = tau_t+tau_v

    sigma_vm =  np.sqrt(sigma_b**2 + 3 * tau_combined**2)

    return sigma_vm


def fos_calculation(V, M ,T, Sy, Kt, Kts ,d_out , d_in):
        sigma_vm = von_mises_stress(d_out, d_in, V, M, T, Kt, Kts)
        return Sy / sigma_vm 


def solve_required_diameter(V, M, T, Sy, Kt, Kts, target_fos , d_inner):

    # diamater will prolly be between these bounds
    d_low = d_inner
    d_high = 5.0
    d_mid = 0

    for _ in range(100):
        d_mid = 0.5 * (d_low + d_high)
        fos = fos_calculation(V, M, T, Sy,  Kt, Kts, d_mid , d_inner)

        # Runs until fos is withing a certain tolerance or 100 iterations
        if abs(fos - target_fos) < 1e-5:
            break

        # binary search for the fos
        if  fos > target_fos:
            d_high = d_mid
        else:
            d_low = d_mid

    return d_mid

