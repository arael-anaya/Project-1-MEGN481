import DiameterCalculations
import keywayCalculations
import StressConcentration
import snapRingCalculation
import diameterSnap

from dataclasses import dataclass
from typing import Dict, Any, List
import numpy as np
import copy

MAX_ITER = 20
TOL = 1e-7



@dataclass
class Segment:
    name: str
    V: float
    M: float
    T: float
    link: str = ""
    r_ratio: float = 0.05
    fos: float = 0.0

    d: float = 1.0
    Kt: float = 1.0
    Kts: float = 1.0

    def update_stress_concentration(self, linked_segment, r):
        if linked_segment is None:
            return

        D, d = max(self.d, linked_segment.d), min(self.d, linked_segment.d)

        self.Kt = StressConcentration.stress_concentration(D, d, r, "bending")
        self.Kts = StressConcentration.stress_concentration(D, d, r, "torsion")

    def print_geometry(self, segments):
        """
        Print geometric ratios for this segment's shoulder transition.
        Requires full segments dict to access linked segment.
        """

        if not self.link:
            return

        linked = segments[self.link]

        D = max(self.d, linked.d)
        d = min(self.d, linked.d)

        r = self.r_ratio * d

        d_over_D = d / D
        r_over_d = r / d

        print(f"{self.name} -> {self.link}")
        print(f"  D = {D:.4f} in")
        print(f"  d = {d:.4f} in")
        print(f"  r = {r:.4f} in")
        print(f"  d/D = {d_over_D:.4f}") 
        print(f"  r/d = {r_over_d:.4f}\n")

        


@dataclass
class Material:
    name: str
    Sy_psi: float


def solve_shaft_iterative(segments, Sy, target_fos, tol=1e-7, max_iter=50):

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
                r_actual = seg.r_ratio * d_small
                seg.update_stress_concentration(linked_seg, r_actual)

                

        if max_change < tol:
            # print("Converged.")
            break

    return segments

def solve_shaft_discrete(segments, Sy, target_fos,
                        tol=1e-7, max_outer_iter=20):

    for _ in range(max_outer_iter):

        segments = solve_shaft_iterative(
            segments,
            Sy,
            target_fos,
            tol,
            max_outer_iter
        )


        changed = diameterSnap.snap_all_diameters(segments , "norm")


        if not changed:
            print("Discrete solution converged.")
            break

    return segments

def build_segments():
    return {
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
            176, 1254, 426.5
        ),
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
        ),
        "Snap Ring" : Segment(
            "Snap Ring" ,
            602,995,-462.5,
            Kt = 3,
            Kts = 5 
            )

    }

def optimize_radii(Sy, target_fos,
                    r_min=0.02,
                    r_max=0.10,
                    r_steps=9,
                    max_passes=5,
                    initial_r=0.05):
    """
    Coordinate-descent optimization of fillet radii.
    Returns optimized segments dictionary.
    """

    r_values = np.linspace(r_min, r_max, r_steps)

    segments = build_segments()

    # initialize radii
    for seg in segments.values():
        seg.r_ratio = initial_r

    linked_names = [name for name, seg in segments.items() if seg.link]

    for outer_iter in range(max_passes):
        radii_changed = False
        for name in linked_names:
        
            local_best_r = segments[name].r_ratio
            local_best_metric = float("inf")

            for r_trial in r_values:

                trial_segments = copy.deepcopy(segments)

                # copy current radii
                for n in linked_names:
                    trial_segments[n].r_ratio = segments[n].r_ratio

                # vary only this shoulder
                trial_segments[name].r_ratio = r_trial

                trial_segments = solve_shaft_discrete(
                    trial_segments,
                    Sy,
                    target_fos
                )

                total_d = sum(s.d for s in trial_segments.values())

                if total_d < local_best_metric:
                    local_best_metric = total_d
                    local_best_r = r_trial

            if abs(segments[name].r_ratio - local_best_r) > 1e-6:
                radii_changed = True

            segments[name].r_ratio = local_best_r

        if not radii_changed:

            break

    segments = solve_shaft_discrete(segments, Sy, target_fos)

    return segments

def main():

    r_min = 0.02
    r_max = 0.10
    r_steps = 9


    target_fos_list = [2.0]
    materials = [Material("4140 Steel", Sy_psi=60200)]
    key_materials = [Material("FILL IN NAME", Sy_psi=41300)]
    fos_key_diff = 1.0

    for target_fos in target_fos_list:
        for material in materials:

            Sy = material.Sy_psi

            segments = build_segments()
            # segments = optimize_radii(Sy, target_fos , r_min, r_max , r_steps, MAX_ITER)

            segments = solve_shaft_discrete(segments, Sy, target_fos, TOL, MAX_ITER)

            shaft_fos_values = []
            for seg in segments.values():
                seg.fos = DiameterCalculations.fos_calculation(
                    seg.V, seg.M, seg.T,
                    Sy, seg.Kt, seg.Kts, seg.d
                )
                shaft_fos_values.append(seg.fos)

            gear_d = segments["Gear Shoulder"].d
            T_key = segments["Gear Shoulder"].T

            
            
            snapRing = segments["Snap Ring"]

            snapRing.d, snapRing.fos = snapRingCalculation.solve_discrete_snap_ring(
                snapRing.V,
                snapRing.M,
                snapRing.T,
                Sy,
                snapRing.Kt,
                snapRing.Kts,
                target_fos,
                gear_d
            )
            
            shaft_fos_values.append(snapRing.fos)

            min_shaft_fos = min(shaft_fos_values)

            Sy_key = key_materials[0].Sy_psi
            
            key_target_fos = min_shaft_fos - fos_key_diff

            bounds_L = (0.5, 1.25)
            bounds_w = (0.05, 0.5)
            bounds_H = (0.05, 0.5)

            L_opt, w_opt, H_opt, key_true_fos = keywayCalculations.discrete_key_design(
                T_key, gear_d, Sy_key, key_target_fos,
                bounds_L, bounds_w, bounds_H
            )

            print("\n" + "="*100)
            print("FINAL SHAFT DESIGN REPORT")
            print("="*100)

            print(f"\nMaterial: {material.name}")
            print(f"Yield Strength (Sy): {Sy:.2f} psi")
            print(f"Design  Factor:    {target_fos:.4f}")
            print("-"*100)

            for seg in segments.values():

                if seg.name == "Snap Ring":
                    continue

                print(f"\nSEGMENT: {seg.name}")
                print("-"*80)

                print(f"Diameter (d):        {seg.d:.4f} in")
                print(f"Kt (bending):        {seg.Kt:.4f}")
                print(f"Kts (torsion):       {seg.Kts:.4f}")
                print(f"True FoS:            {seg.fos:.4f}")

                if seg.link:
                    linked = segments[seg.link]

                    D = max(seg.d, linked.d)
                    d_small = min(seg.d, linked.d)
                    r = seg.r_ratio * d_small

                    print(f"Fillet Radius (r):   {r:.4f} in")
                    print(f"d/D:                 {(d_small / D):.4f}")
                    print(f"r/D:                 {(r / D):.4f}")
                else:
                    print(f"Fillet Radius:       N/A")
                    print(f"d/D:                 N/A")
                    print(f"r/D:                 N/A")

            print("\n" + "="*100)
            print("SNAP RING RESULTS")
            print("="*100)

            print(f"Snap Ring Outer Diameter:  {snapRing.d:.4f} in")
            print(f"Snap Ring Inner Diameter:  {gear_d:.4f} in")
            print(f"Snap Ring Kt:        {snapRing.Kt:.4f}")
            print(f"Snap Ring Kts:       {snapRing.Kts:.4f}")
            print(f"Snap Ring True FoS:  {snapRing.fos:.4f}")

            print("\nMinimum Governing FoS: "
                f"{min_shaft_fos:.4f}")

            print("\n" + "="*100)
            print("KEY DESIGN RESULTS")
            print("="*100)

            print(f"Gear Shaft Diameter: {gear_d:.4f} in")
            print(f"Target Key FoS:      {key_target_fos:.4f}")
            print(f"Key Length (L):      {L_opt:.4f} in")
            print(f"Key Width (w):       {w_opt:.4f} in")
            print(f"Key Height (H):      {H_opt:.4f} in")
            print(f"True Key FoS:        {key_true_fos:.4f}")

            print("\n" + "="*100)
            print("END OF REPORT")
            print("="*100 + "\n")


if __name__ == "__main__":
    main()


