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
import diameterSnap





def von_mises_stress(d_out, d_in, V, M, T, Kt, Kts):
    pi = np.pi

    J = (pi / 32) * (d_out**4 - d_in**4)
    I = (pi / 64) * (d_out**4 - d_in**4)
    c = d_out / 2

    sigma_b = Kt * (c * M / I)
    tau_t = Kts * (c * T / J)

    tau_v = 16 * V / (3 * pi * (d_out**2 - d_in**2))

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

def solve_discrete_snap_ring(
    V,
    M,
    T,
    Sy,
    Kt,
    Kts,
    target_fos,
    inner_diameter,
    tol=1e-7,
    max_iter=50
):
    """
    Solves required snap ring outer diameter,
    snaps to catalog size,
    and guarantees FoS >= target_fos.
    """

    # --- 1) Continuous solve ---
    d_required = solve_required_diameter(
        V, M, T,
        Sy, Kt, Kts,
        target_fos,
        inner_diameter
    )

    # --- 2) Snap to catalog OD ---
    d_snapped = diameterSnap.snap_diameter(d_required, "snapRing")

    # --- 3) Recalculate FoS ---
    fos = fos_calculation(
        V, M, T,
        Sy, Kt, Kts,
        d_snapped,
        inner_diameter
    )

    # --- 4) If FoS too low, step up catalog sizes ---
    while fos < target_fos:

        # bump slightly to force next catalog size
        d_snapped += 1e-6
        d_snapped = diameterSnap.snap_diameter(d_snapped, "snapRing")

        fos = fos_calculation(
            V, M, T,
            Sy, Kt, Kts,
            d_snapped,
            inner_diameter
        )

    return d_snapped, fos


