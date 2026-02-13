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


def von_mises_stress(d, V, M, T, Kt, Kts):
    pi = np.pi

    J = (pi / 32) * d**4
    I = (pi / 64) * d**4
    c = d / 2

    sigma_b = Kt * (c * M / I)
    tau_t = Kts * (c * T / J)

    tau_v = 16 * V / (3 * pi * d**2)

    tau_combined = tau_t+tau_v

    sigma_vm =  np.sqrt(sigma_b**2 + 3 * tau_combined**2)

    return sigma_vm

def fos_calculation(V, M ,T, Sy, Kt, Kts ,d):
        sigma_vm = von_mises_stress(d, V, M, T, Kt, Kts)
        return Sy / sigma_vm 

def solve_required_diameter(V, M, T, Sy, Kt, Kts, target_fos):

    # diamater will prolly be between these bounds
    d_low = 0.1
    d_high = 5.0
    d_mid = 0

    for _ in range(100):
        d_mid = 0.5 * (d_low + d_high)
        fos = fos_calculation(V, M, T, Sy,  Kt, Kts, d_mid)

        # Runs until fos is withing a certain tolerance or 100 iterations
        if abs(fos - target_fos) < 1e-5:
            break

        # binary search for the fos
        if  fos > target_fos:
            d_high = d_mid
        else:
            d_low = d_mid

    return d_mid

