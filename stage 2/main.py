import DiameterCalculations
import keywayCalculations
import StressConcentration

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np


STANDARD_DIAMETERS = STANDARD_DIAMETERS = [
    0.25,   # 1/4"
    0.375,  # 3/8"
    0.5,    # 1/2"
    0.625,  # 5/8"
    0.75,   # 3/4"
    1.0,    # 1"
    1.25    # 1 1/4"
]


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


def solve_shaft_iterative(segments, Sy, target_fos, r, tol=1e-7, max_iter=50):

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
                linked_seg = segments[seg.link]
                d_small = min(seg.d, linked_seg.d)
                seg.update_stress_concentration(linked_seg, r * d_small)
                

        if max_change < tol:
            print("Converged.")
            break

    return segments



def snap_all_diameters(segments):

    def snap_diameter(d_required):
        for d_std in STANDARD_DIAMETERS:
            if d_std >= d_required:
                return d_std
        raise ValueError("Required diameter exceeds available standard sizes.")

    changed = False
    for seg in segments.values():
        d_old = seg.d
        seg.d = snap_diameter(seg.d)

        if abs(seg.d - d_old) > 1e-9:
            changed = True
    return changed


def solve_shaft_discrete(segments, Sy, target_fos, r,
                        tol=1e-7, max_outer_iter=20):

    for _ in range(max_outer_iter):

        segments = solve_shaft_iterative(
            segments,
            Sy,
            target_fos,
            r,
            tol=tol
        )

        changed = snap_all_diameters(segments)


        if not changed:
            print("Discrete solution converged.")
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
    key_materials = [ Material("FILL IN NAME" , Sy_psi = 41300)]
    fos_key_diff = .5

    for target_fos in target_fos_list:
        for material in materials:

            Sy = material.Sy_psi
            print(f"\nTarget FoS = {target_fos}")
            print(f"{material.name} Sy = {Sy} psi\n")

            # Iterte through r = .02 to r = .1
            r = 0.05

            segments = solve_shaft_discrete(
                segments,
                Sy,
                target_fos,
                r
            )

            shaft_fos_values = []
            for seg in segments.values():

                fos_actual = DiameterCalculations.fos_calculation(
                    seg.V,
                    seg.M,
                    seg.T,
                    Sy,
                    seg.Kt,
                    seg.Kts,
                    seg.d
                )
                shaft_fos_values.append(fos_actual)
                print(f"{seg.name}")
                print(f"  Diameter = {seg.d:.4f} in")
                print(f"  Kt = {seg.Kt:.3f}")
                print(f"  Kts = {seg.Kts:.3f}")
                print(f"  Actual FoS = {fos_actual:.4f}\n")

            min_shaft_fos = min(shaft_fos_values)
                
            print("\n--- KEY DESIGN ---")

            # Shaft diameter and torque at gear location
            gear_d = segments["Gear Shoulder"].d
            T_key = segments["Gear Shoulder"].T

            key_target_fos = min_shaft_fos - fos_key_diff
            Sy_key = key_materials[0].Sy_psi


            bounds_L = (0.5, 1.25)       # inches
            bounds_w = (0.05, 0.5)      # inches
            bounds_H = (0.05, 0.5)      # inches
        

            L_opt, w_opt, H_opt , key_true_fos = keywayCalculations.discrete_key_design(
                T_key,
                gear_d,
                Sy_key,
                key_target_fos,
                bounds_L,
                bounds_w,
                bounds_H
            )


            print(f"Gear shaft diameter = {gear_d:.4f} in")
            print(f"Optimized Key Geometry:")
            print(f"  L = {L_opt:.4f} in")
            print(f"  w = {w_opt:.4f} in")
            print(f"  H = {H_opt:.4f} in")
            print(f"Key FOS = {key_true_fos:.4f}")

if __name__ == "__main__":
    main()


