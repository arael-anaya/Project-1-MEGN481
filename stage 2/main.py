import DiameterCalculations
import keywayCalculations
import StressConcentration

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np

@dataclass
class Segment:
    name: str
    V: float
    M: float
    T: float
    link: str = ""

    d: float = 1.0
    Kt: float = 1.0
    Kts: float = 1.0

    def update_stress_concentration(self, linked_segment, r):
        if linked_segment is None:
            return

        D = linked_segment.d
        d = self.d


        self.Kt = StressConcentration.stress_concentration(D, d, r, "bending")
        self.Kts = StressConcentration.stress_concentration(D, d, r, "torsion")


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

def solve_shaft_iterative(segments, Sy, target_fos, r, tol=1e-4, max_iter=50):

    for _ in range(max_iter):

        max_change = 0


        for seg in segments.values():

            d_old = seg.d

            seg.d = DiameterCalculations.solve_required_diameter(
                seg.V, seg.M, seg.T,
                Sy, seg.Kt, seg.Kts,
                target_fos
            )

            max_change = max(max_change, abs(seg.d - d_old))

        # Step 2 — update stress concentrations
        for seg in segments.values():
            if seg.link:
                seg.update_stress_concentration(segments[seg.link], r)

        if max_change < tol:
            print("Converged.")
            break

    return segments




def main():

    segments = {
    "Center Section": Segment("Center Section", 176, 1254, 925),

    "Bearing 1 Shoulder": Segment(
        "Bearing 1 Shoulder",
        176, 203, 462.5,
        link="Center Section"
    ),

    "Output Spline Shoulder": Segment(
        "Output Spline Shoulder",
        97, 170, 462.5,
        link="Bearing 1 Shoulder"
    ),

    "Bearing 2 Shoulder": Segment(
        "Bearing 2 Shoulder",
        602, 300, -462.5,
        link="Center Section"
    ),

    "Input Spline Shoulder": Segment(
        "Input Spline Shoulder",
        97, 170, -462.5,
        link="Bearing 2 Shoulder"
    ),
    }
    
    target_fos_list = [2.0]   # <-- SET REQUIRED DESIGN FACTOR HERE

    materials = [ Material("4140 Steel" , Sy_psi = 60200)] # < --- SET MATERIAL HERE

    for target_fos in target_fos_list:
        for material in materials:

            Sy = material.Sy_psi
            print(f"\nTarget FoS = {target_fos}")
            print(f"{material.name} Sy = {Sy} psi\n")

            r = 0.06 

            segments = solve_shaft_iterative(
            segments,
            Sy,
            target_fos,
            r
            )

            for seg in segments.values():
                print(f"{seg.name}")
                print(f"  Diameter = {seg.d:.4f} in")
                print(f"  Kt = {seg.Kt:.3f}")
                print(f"  Kts = {seg.Kts:.3f}\n")

            
            # worst_d = 0
            # worst_loc = None

            # for row in table:
            
            # DO NOT WORRY ABOUT THIS IT JUST TAKES THE V, M, and T FROM EACH ROW OF THE DICTIONARY
            # V = worst_case_value(row["V"])
            # M = worst_case_value(row["M"])
            # T = worst_case_value(row["T"])
            # Kt = worst_case_value(row["Kt"])
            # Kts = worst_case_value(row["Kts"])

            # if row["Location"] == "Keyway":
            #     # you need a shaft diameter first
            #     d_key = 1.125  # or whatever you computed
            #     L = 1.5        # assumed key length
            #     w = 0.25       # key width
            #     H_required = keywayCalculations.optimize_key_height(
            #         T, d_key, L, w, Sy, target_fos
            #     )
            #     print(f"{row['Location']}")
            #     print(f"  Required Height = {H_required:.4f} in\n")
                
            #     continue

            # fos = DiameterCalculations.fos_calculation(V, M, T, Sy, Kt, Kts , d_req)

            # print(f"{row['Location']}")
            # print(f"  Required diameter = {d_req:.4f} in\n")


        # Filler to find the worst fos in the shaft etc etc
        #     if d_req > worst_d:
        #         worst_d = d_req
        #         worst_loc = row["Location"]

        # print(f"Worst-case location: {worst_loc}")
        # print(f"Governing diameter required: {worst_d:.4f} in\n")
        # print(f"------------------------------------------------------------------ \n")

if __name__ == "__main__":
    main()


