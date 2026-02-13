import DiameterCalculations
import keywayCalculations

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

def main():

    table = [
        {"Location": "Output Spline 1 Shoulder (spline side)", "V": 97, "M": 170, "T": 462.5 , "Kt" : 1.0 , "Kts" : 1.0},
        {"Location": "Bearing 1 Shoulder (bearing side)", "V": 176, "M": 203, "T": 462.5 , "Kt" : 1.0 , "Kts" : 1.0},
        {"Location": "Gear Shoulder (gear side)", "V": 176, "M": 1254, "T": 925, "Kt" : 1.0 , "Kts" : 1.0}, #Jordan said to use 925 here but we should check that

        # Ignore Keyway and Snap Ring "diameter calculations for now"
        {"Location": "Keyway", "V": 602, "M": 1363, "T": -462.5 , "Kt" : 2.3 , "Kts": 3.0 }, #Jordan said to use 602 for shear cause its max
        {"Location": "Snap Ring for Gear", "V": 602, "M": 995, "T": -462.5 , "Kt" : 3.0 , "Kts" : 5.0},


        {"Location": "Bearing 2 Shoulder (bearing side)", "V": 602, "M": 300, "T": -462.5 , "Kt" :2.066 , "Kts" : 1.732},
        {"Location": "Input Spline 2 Shoulder (spline side)", "V": 97, "M": 170, "T": -462.5 , "Kt" : 1.0 , "Kts" : 1.0},
    ]
    
    target_fos_list = [2.0]   # <-- SET REQUIRED DESIGN FACTOR HERE

    materials = [Material("1020 Steel", Sy_psi=30000) , Material("4140 Steel" , Sy_psi = 60200)] # < --- SET MATERIAL HERE





    for target_fos in target_fos_list:
        for material in materials:

            Sy = material.Sy_psi
            print(f"\nTarget FoS = {target_fos}")
            print(f"{material.name} Sy = {Sy} psi\n")
            
            # worst_d = 0
            # worst_loc = None

            for row in table:
            
                # DO NOT WORRY ABOUT THIS IT JUST TAKES THE V, M, and T FROM EACH ROW OF THE DICTIONARY
                V = worst_case_value(row["V"])
                M = worst_case_value(row["M"])
                T = worst_case_value(row["T"])
                Kt = worst_case_value(row["Kt"])
                Kts = worst_case_value(row["Kts"])

                if row["Location"] == "Keyway":
                    # you need a shaft diameter first
                    d_key = 1.125  # or whatever you computed

                    L = 1.5        # assumed key length
                    w = 0.25       # key width

                    H_required = keywayCalculations.optimize_key_height(
                        T, d_key, L, w, Sy, target_fos
                    )

                    print(f"{row['Location']}")
                    print(f"  Required Height = {H_required:.4f} in\n")

                    continue

                #finds the correct diamater for each of the shaft segments
                d_req = DiameterCalculations.solve_required_diameter(V, M, T, Sy, Kt, Kts , target_fos)

                # finds the fos with the chosen diameter SIMPLY TO DOUBLE CHECK
                # fos = DiameterCalculations.fos_calculation(V, M, T, Sy, Kt, Kts , d_req)

                print(f"{row['Location']}")
                print(f"  Required diameter = {d_req:.4f} in\n")


            # Filler to find the worst fos in the shaft etc etc
            #     if d_req > worst_d:
            #         worst_d = d_req
            #         worst_loc = row["Location"]

            # print(f"Worst-case location: {worst_loc}")
            # print(f"Governing diameter required: {worst_d:.4f} in\n")
            # print(f"------------------------------------------------------------------ \n")

if __name__ == "__main__":
    main()
