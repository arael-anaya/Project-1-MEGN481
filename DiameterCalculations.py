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


def main():

    table = [
        {"Location": "Output Spline 1 Shoulder (spline side)", "V": 97, "M": 170, "T": 462.5 , "Kt" : 1.0 , "Kts" : 1.0},
        {"Location": "Bearing 1 Shoulder (bearing side)", "V": 176, "M": 203, "T": 462.5 , "Kt" : 1.0 , "Kts" : 1.0},
        {"Location": "Gear Shoulder (gear side)", "V": 176, "M": 1254, "T": 925, "Kt" : 1.0 , "Kts" : 1.0}, #Jordan said to use 900 here but we should check that
        {"Location": "Keyway", "V": "176/602", "M": 1363, "T": -462.5 , "Kt" : 2.3 , "Kts": 3.0 }, #Jordan said to use 
        {"Location": "Snap Ring for Gear", "V": 602, "M": 995, "T": -462.5 , "Kt" : 3.0 , "Kts" : 5.0},
        {"Location": "Bearing 2 Shoulder (bearing side)", "V": 602, "M": 300, "T": -462.5 , "Kt" : 1.0 , "Kts" : 1.0},
        {"Location": "Input Spline 2 Shoulder (spline side)", "V": 97, "M": 170, "T": -462.5 , "Kt" : 1.0 , "Kts" : 1.0},
    ]
    
    target_fos_list = [3.0 , 2.0]   # <-- SET REQUIRED DESIGN FACTOR HERE

    materials = [Material("Steel", Sy_psi=60000) , Material("Alluminium" , Sy_psi = 9000)] # < --- SET MATERIAL HERE





    for target_fos in target_fos_list:
        for material in materials:

            Sy = material.Sy_psi
            print(f"\nTarget FoS = {target_fos}")
            print(f"Material Sy = {Sy} psi\n")
            
            worst_d = 0
            worst_loc = None

            for row in table:

                # DO NOT WORRY ABOUT THIS IT JUST TAKES THE V, M, and T FROM EACH ROW OF THE DICTIONARY
                V = worst_case_value(row["V"])
                M = worst_case_value(row["M"])
                T = worst_case_value(row["T"])
                Kt = worst_case_value(row["Kt"])
                Kts = worst_case_value(row["Kts"])

                #finds the correct diamater for each of the shaft segments
                d_req = solve_required_diameter(V, M, T, Sy, Kt, Kts , target_fos)

                #finds the fos with the chosen diameter SIMPLY TO DOUBLE CHECK
                fos = fos_calculation(V, M, T, Sy, Kt, Kts , d_req)

                print(f"{row['Location']}")
                print(f"  Required diameter = {d_req:.4f} in")
                print(f"  FOS = {fos:.4f} in\n")

                if d_req > worst_d:
                    worst_d = d_req
                    worst_loc = row["Location"]

            print(f"Worst-case location: {worst_loc}")
            print(f"Governing diameter required: {worst_d:.4f} in\n")
            print(f"------------------------------------------------------------------ \n")

if __name__ == "__main__":
    main()
