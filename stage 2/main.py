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

        D, d = max(self.d, linked_segment.d), min(self.d, linked_segment.d)

        self.Kt = StressConcentration.stress_concentration(D, d, r, "bending")
        self.Kts = StressConcentration.stress_concentration(D, d, r, "torsion")


@dataclass
class Material:
    name: str
    Sy_psi: float


def solve_shaft_iterative(segments, Sy, target_fos, r, tol=1e-7, max_iter=50000):

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
                linked_seg = segments[seg.link]
                d_small = min(seg.d, linked_seg.d)
                seg.update_stress_concentration(linked_seg, r * d_small)

                

        if max_change < tol:
            print("Converged.")
            break

    return segments




def main():

    segments = {
    "Output Spline Shoulder": Segment(
        "Output Spline Shoulder",
        97, 170, 462.5,
        link="Bearing 1 Shoulder"
    ),

    "Bearing 1 Shoulder": Segment(
        "Bearing 1 Shoulder",
        176, 203, 462.5,
        link="Center Section"
    ),

    "Center Section": Segment(
        "Center Section", 
        176, 1254, 426.5),

     "Gear Shoulder": Segment(
        "Gear Shoulder",
        176, 1254, 925,
        link="Center Section"
    ),

    "Bearing 2 Shoulder": Segment(
        "Bearing 2 Shoulder",
        602, 300, -462.5,
        link="Gear Shoulder"
    ),

    "Input Spline Shoulder": Segment(
        "Input Spline Shoulder",
        97, 170, -462.5,
        link="Bearing 2 Shoulder"
    )


    }
    
    target_fos_list = [2.0]   # <-- SET REQUIRED DESIGN FACTOR HERE

    materials = [ Material("4140 Steel" , Sy_psi = 60200)] # < --- SET MATERIAL HERE

    for target_fos in target_fos_list:
        for material in materials:

            Sy = material.Sy_psi
            print(f"\nTarget FoS = {target_fos}")
            print(f"{material.name} Sy = {Sy} psi\n")


            # Iterte through r = .02 to r = .1
            r = 0.05 #a secret * diameter that I added in #Step 2 — update stress concentrations

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

if __name__ == "__main__":
    main()


