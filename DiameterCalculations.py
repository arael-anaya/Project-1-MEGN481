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





@dataclass
class Material:
    name: str
    Sy_psi: float


def worst_case_value(v: Any) -> float:
    if isinstance(v, (int, float, np.number)):
        return float(abs(v))

    s = str(v).strip()
    parts = [p.strip() for p in s.replace(",", "/").split("/")]
    nums = [abs(float(p)) for p in parts if p != ""]
    return max(nums) if nums else 0.0


def von_mises_stress(d, V, M, T, Kt, Kts):
    pi = np.pi

    J = (pi / 32) * d**4
    I = (pi / 64) * d**4
    c = d / 2

    sigma_b = Kt * (c * M / I)
    tau_t = Kts * (c * T / J)
    tau_v =0.0
    # tau_v = 16 * V / (3 * pi * d**2)

    tau_combined = tau_t+tau_v

    sigma_vm = np.sqrt(sigma_b**2 + 3 * tau_combined**2)
    return sigma_vm


def solve_required_diameter(V, M, T, Sy, Kt, Kts  , target_fos):
    """
    Solve for d such that FoS = target_fos.
    """

    def fos_objective(d):
        sigma_vm = von_mises_stress(d, V, M, T, Kt, Kts)
        return Sy / sigma_vm - target_fos

    # diamater will prolly be between these bounds
    d_low = 0.1
    d_high = 5.0

    for _ in range(100):
        d_mid = 0.5 * (d_low + d_high)

        # binary search for the fos
        if fos_objective(d_mid) > 0:
            d_high = d_mid
        else:
            d_low = d_mid

    return d_mid


def main():

    table = [
        {"Location": "Output Spline 1 Shoulder (spline side)", "V": 97, "M": 170, "T": 462.5},
        {"Location": "Bearing 1 Shoulder (bearing side)", "V": 176, "M": 203, "T": 462.5},
        {"Location": "Gear Shoulder (gear side)", "V": 176, "M": 1254, "T": "-462 / 0 / 462 / 925"},
        {"Location": "Keyway", "V": "176/602", "M": 1363, "T": -462.5},
        {"Location": "Snap Ring for Gear", "V": 602, "M": 995, "T": -462.5},
        {"Location": "Bearing 2 Shoulder (bearing side)", "V": 602, "M": 300, "T": -462.5},
        {"Location": "Input Spline 2 Shoulder (spline side)", "V": 97, "M": 170, "T": -462.5},
    ]
    
    target_fos = 3.0   # <-- SET REQUIRED DESIGN FACTOR HERE

    mat = Material("Steel", Sy_psi=60000) # < --- SET MATERIAL HERE

    Kt = 2.3
    Kts = 3.0

    print(f"\nTarget FoS = {target_fos}")
    print(f"Material Sy = {mat.Sy_psi} psi\n")

    worst_d = 0
    worst_loc = None

    for row in table:

        # DO NOT WORRY ABOUT THIS IT JUST TAKES THE V, M, and T FROM EACH ROW OF THE DICTIONARY
        V = worst_case_value(row["V"])
        M = worst_case_value(row["M"])
        T = worst_case_value(row["T"])


        #finds the correct diamater for each of the shaft segments
        d_req = solve_required_diameter(V, M, T, mat.Sy_psi, Kt, Kts , target_fos)

        print(f"{row['Location']}")
        print(f"  Required diameter = {d_req:.4f} in\n")

        if d_req > worst_d:
            worst_d = d_req
            worst_loc = row["Location"]

    print(f"Worst-case location: {worst_loc}")
    print(f"Governing diameter required: {worst_d:.4f} in\n")


if __name__ == "__main__":
    main()
